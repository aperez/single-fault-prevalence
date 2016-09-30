import os
import uuid
import shutil

import classifier.process as process
from .commit_cutoff import *

from git import Repo

class GitRepo(object):
    def __init__(self):
        self.folder = None
        self.repo = None
        self.branch = None

    def clone(self, url, folder=os.getcwd(), extra_args=''):
        if len(extra_args) > 0:
            extra_args = extra_args + ' '

        self.folder = folder + '/' + str(uuid.uuid4())
        ret = process.call("git clone {}{} {}".format(extra_args, url, self.folder))
        if ret == 0:
            self.repo = Repo(self.folder)
            self.branch = self.repo.active_branch.name

    def diff(self, commit):
        return self.repo.git.diff(commit)

    def checkout(self, commit, force=True):
        params = [commit]
        if force:
            params.insert(0, '-f')
        self.repo.git.checkout(*params)

    def iter_commits(self, branch=None, cutoff=CommitCutoff()):
        """ Iterates through commits in a branch from newest to oldest. """
        if self.repo:
            if not branch:
                branch = self.branch
            cutoff.reset()
            for commit in self.repo.iter_commits(branch):
                if not cutoff.cutoff(commit):
                    yield commit

    def get_folder(self):
        return self.folder

    def remove(self):
        if self.folder:
            shutil.rmtree(self.folder, ignore_errors=True)
