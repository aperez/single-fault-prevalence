import operator

from classifier.spectra import *
from .similarity_function import *

class SimilarityRanker(object):
    def __init__(self, heuristic=ochiai):
        self.heuristic = heuristic

    def rank(self, spectrum, spectrum_filter=None):
        return self.rank_multiple(spectrum, [self.heuristic], spectrum_filter)[0]

    def rank_multiple(self, spectrum, heuristics, spectrum_filter=None):
        rankings = [[] for x in range(len(heuristics))]
        for c, n in self.iterate(spectrum, spectrum_filter):
            for i in range(len(heuristics)):
                rankings[i].append((c, heuristics[i](n)))

        for i, ranking in enumerate(rankings):
            rankings[i] = sorted(ranking, key=operator.itemgetter(1), reverse=True)
        return rankings

    def iterate(self, spectrum, spectrum_filter=None):
        if not spectrum_filter:
            spectrum_filter = SpectrumFilter(spectrum)

        error = {}
        for t in spectrum_filter.transactions_filter:
            error[t] = spectrum.is_error(t)

        for c in spectrum_filter.components_filter:
            n = [[0, 0], [0, 0]]

            for t in spectrum_filter.transactions_filter:
                activity = spectrum.get_activity(t, c)
                n[1 if activity else 0][1 if error[t] else 0] += 1

            yield c, n

    def collapsed_score(self, spectrum, spectrum_filter, heuristics):
        n = [[0, 0], [0, 0]]

        for t in spectrum_filter.transactions_filter:
            error = spectrum.is_error(t)

            activity = 0
            for c in spectrum_filter.components_filter:
                activity += spectrum.get_activity(t, c)

            n[1 if activity > 0 else 0][1 if error else 0] += 1
        scores = []
        for heuristic in heuristics:
            scores.append(heuristic(n))
        return scores

def calculate_cd(rank, component):
    best = 0
    same = 0
    current = None
    found = False

    for ci, value in rank:
        if current == None:
            current = value
        elif current == value:
            same += 1
        else:
            if found:
                break
            best += same + 1
            same = 0
            current = value
        if ci == component:
            found = True

    if not found:
        return best + same + 1, current
    return best + (same / 2), current

def calculate_cd_from_score(rank, score):
    best = 0
    same = 0

    for _, value in rank:
        if value > score:
            best += 1
        elif value == score:
            same += 1
        else:
            break

    return best + (same / 2)

def normalized_cd(rank, component):
    cd, value = calculate_cd(rank, component)
    return div(cd, len(rank)), value

def normalized_cd_from_score(rank, score):
    return div(calculate_cd_from_score(rank, score), len(rank))
