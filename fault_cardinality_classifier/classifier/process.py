import subprocess
import threading

SUBPROCESS_TIMEOUT = 900

def call(cmd, timeout=SUBPROCESS_TIMEOUT, **arguments):
    pipe = subprocess.DEVNULL
    # stdout=pipe, stderr=pipe
    proc = subprocess.Popen(cmd.split(' '), **arguments)
    proc_thread = threading.Thread(target=proc.communicate)
    proc_thread.start()
    proc_thread.join(timeout)
    if proc_thread.is_alive():
        try:
            proc.kill()
        except OSError as e:
            return proc.returncode
        return 1
    return proc.returncode
