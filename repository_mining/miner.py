import sys
import os
import uuid

import unqlite

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + \
                '/../fault_cardinality_classifier/')
import classifier

SUBJECTS = os.path.dirname(os.path.abspath(__file__)) + '/../subjects/output/subjects_final.txt'

def generate_db_name(repo_url):
    name = repo_url
    if repo_url.endswith('.git'):
        name = name[:-4]

    return "../database/{}.db".format(name[name.rfind("/")+1:])

def mine_repo(repo_url, cutoff=classifier.CommitCutoff()):
    dbpath = generate_db_name(repo_url)
    db = unqlite.UnQLite(dbpath)

    gr = classifier.GitRepo()
    gr.clone(repo_url, extra_args='--single-branch')
    db['URL'] = repo_url

    commits_collection = db.collection('commits')
    commits_collection.drop()
    commits_collection.create()

    fixes_collection = db.collection('fixes')
    fixes_collection.drop()
    fixes_collection.create()
    analysis = classifier.FixAnalysis(fixes_collection)

    current_spectra = None
    counter = 0

    for commit in gr.iter_commits(cutoff=cutoff):
        counter = counter + 1

        try:
            if not current_spectra:
                spectra = classifier.CommitSpectra(gr, commit)
                if not spectra.is_valid(): continue
                spectra.store(commits_collection)

                if spectra.is_passing():
                    current_spectra = spectra
            else:
                print('testing commit ', commit)
                diff = current_spectra.diff(commit)

                spectra = classifier.CommitSpectra(gr, commit)
                if not spectra.is_valid(): continue
                spectra.store(commits_collection)

                result = analysis.analyze(diff, spectra, current_spectra)
                skip = skip and not result

                if spectra.is_passing():
                    current_spectra = spectra
        except:
            pass

    db['counter'] = counter
    gr.remove()

if __name__ == '__main__':
    cutoff = classifier.MultipleCommitCutoff(
                classifier.TimeSpanCommitCutoff(days=365),
                classifier.MaxIterationsCommitCutoff(500)
             )

    f = open(SUBJECTS)
    for row in f:
        try:
            repo = "https://github.com/%s/%s.git" % tuple(row.rstrip().split(' '))
            mine_repo(repo, cutoff)
        except:
            pass
