import classifier

class FixAnalysis(object):
    def __init__(self, collection):
        self.collection = collection

    def analyze(self, diff, faulty, fixing):
        faulty.checkout()
        faulty.compile()
        fixing.restore_tests()

        ret = faulty.get_failing_spectrum(fixing.spectra)

        if ret != None:
            spectrum_faulty, spectrum_fixed, location = ret

            # create a filter for the fixed version's spectrum
            sf = classifier.SpectrumFilter(spectrum_fixed)

            # keep modified components according to diff between faulty and fix
            modified = classifier.get_modified_components(diff, spectrum_faulty, spectrum_fixed)

            if len(modified) == 0:
                return False

            sf.keep_components(spectrum_fixed, modified)

            # filter tests that do not fail in faulty version
            tests = spectrum_faulty.get_failing_tests()
            spectrum_fixed.set_failing_tests(tests)
            sf.filter_passing_transactions(spectrum_fixed)

            # filter global ambiguity groups
            sf.filter_ambiguity(spectrum_fixed)

            mhs = classifier.MHS()
            trie = mhs.calculate(spectrum_fixed, spectrum_filter=sf.copy())
            hitting_sets = list(trie)

            classification = str()
            if len(hitting_sets) == 0:
                classification = "not-a-fix"
            elif len(hitting_sets) == 1 and len(hitting_sets[0]) == 1:
                classification = "single-fault"
            else:
                classification = "multiple-fault"

            obj = {'faulty': str(faulty.commit),
                   'fixing': str(fixing.commit),
                   'classification': classification,
                   'mhs': hitting_sets,
                   'filter': sf.to_map(),
                   'location': location,
                   'spectrum': str(spectrum_fixed),
                   'same-tests': faulty.contains_tests(location, tests),
                   'diff': diff}
            self.collection.store(obj)
            return True
        return False
