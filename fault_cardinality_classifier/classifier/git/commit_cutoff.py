import time
import datetime

DELTA_DEFAULT_DAYS = 180 # 6 months

class CommitCutoff(object):
    def reset(self):
        pass

    def cutoff(self, commit):
        return False

class MultipleCommitCutoff(CommitCutoff):
    def __init__(self, *cutoffs):
        self.cutoffs = cutoffs

    def reset(self):
        for cutoff in self.cutoffs:
            cutoff.reset()

    def cutoff(self, commit):
        for cutoff in self.cutoffs:
            if cutoff.cutoff(commit):
                return True
        return False

class MaxIterationsCommitCutoff(CommitCutoff):
    def __init__(self, max_iterations):
        self.max_iterations = max_iterations
        self.reset()

    def reset(self):
        self.iterations = 0

    def cutoff(self, commit):
        self.iterations += 1
        return self.iterations > self.max_iterations

class TimeSpanCommitCutoff(CommitCutoff):
    def __init__(self, *delta_args, **delta_kwargs):
        if len(delta_args) == 0 and len(delta_kwargs) == 0:
            delta_kwargs['days'] = DELTA_DEFAULT_DAYS
        self.delta = datetime.timedelta(*delta_args, **delta_kwargs)
        self.reset()

    def reset(self):
        self.end = None

    def cutoff(self, commit):
        if self.end == None:
            self.end = datetime.datetime.fromtimestamp(commit.committed_date)
        start = datetime.datetime.fromtimestamp(commit.committed_date)
        return abs(self.end - start) > self.delta
