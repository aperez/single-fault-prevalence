import os
import sys
import math
import uuid
import shutil
import subprocess
import threading
from agithub import Github

SUBPROCESS_TIMEOUT=1800 # seconds
NTHREADS=4
PASSES=[]

def read_subjects(subjects_file):
    subjects = open(subjects_file)
    lst = []
    for line in subjects:
        author, repo = line.rstrip().split(' ')[:2]
        lst.append((author, repo))
    subjects.close()
    return lst

def write_subjects(subjects, output_file):
    output = open(output_file, 'w')
    for author, repo in subjects:
        output.write(author + " " + repo + "\n")
    output.close()

def filtering_pass(name):
    def decorator(func):
        def wrapper(subjects, output):
            subs = read_subjects(subjects)
            outlist = []
            func(subs, outlist)
            write_subjects(outlist, output)
        PASSES.append((name, wrapper))
        return wrapper
    return decorator

def call(cmd, **arguments):
    proc = subprocess.Popen(cmd.split(' '), **arguments)
    proc_thread = threading.Thread(target=proc.communicate)
    proc_thread.start()
    proc_thread.join(SUBPROCESS_TIMEOUT)
    if proc_thread.is_alive():
        try:
            proc.kill()
        except OSError as e:
            return proc.returncode
        return 1
    return proc.returncode

def check_maven_thread(subject_chunk, output):
    pipe = subprocess.DEVNULL
    print(subject_chunk)
    for author, repo in subject_chunk:
        cwd = os.getcwd()
        folder = cwd + '/' + str(uuid.uuid4())
        clone_cmd = "git clone https://github.com/{}/{}.git {}".format(author, repo, folder)
        if call(clone_cmd, stdout=pipe, stderr=pipe, cwd=cwd) == 0:
            retval = call("mvn test", stdout=pipe, stderr=pipe, cwd=folder)
            if retval == 0:
                output.append((author, repo))
        shutil.rmtree(folder, ignore_errors=True)

def partition(lst, n):
    if len(lst) >= n:
        n = math.ceil(len(lst) / float(n))
        return [lst[x:x+n] for x in range(0, len(lst), n)]
    else:
        return [lst]

@filtering_pass('Check for pom.xml')
def check_pom(subjects, output):
    g = Github(token=os.environ.get('GITHUB_TOKEN', None))
    for author, repo in subjects:
        status, data = g.repos[author][repo].contents.get()
        if status == 200:
            files = [x['name'].lower() for x in data if x['type'] == 'file']
            if 'pom.xml' in files:
                output.append((author, repo))

@filtering_pass('Run mvn test')
def check_maven(subjects, output):
    subjects = subjects[:4]
    chunks = partition(subjects, NTHREADS)

    threads = []
    for chunk in chunks:
        thread = threading.Thread(target=check_maven_thread, args=(chunk, output))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    force = False
    current_file = 'java_projects.txt'
    filtering_pass_file = 'output/subjects_pass{}.txt'
    final_pass_file = 'output/subjects_final.txt'

    for i, (name, p) in enumerate(PASSES):
        next_pass_file = filtering_pass_file.format(i)
        if force or not os.path.isfile(next_pass_file):
            print("Running pass:", name)
            p(current_file, next_pass_file)
        current_file = next_pass_file

    shutil.copyfile(current_file, final_pass_file)
    print("Wrote subject file", final_pass_file)
