import sys


class SpectrumFilter:
    def __init__(self, spectrum):
        if spectrum:
            self.transactions_filter = \
                [x for x in range(spectrum.transactions)]
            self.components_filter = \
                [x for x in range(spectrum.components)]

    def copy(self):
        sf = SpectrumFilter(None)
        sf.transactions_filter = self.transactions_filter[:]
        sf.components_filter = self.components_filter[:]
        return sf

    def strip_component(self, spectra, component):
        self.transactions_filter = [t for t in self.transactions_filter
                                    if not spectra.get_activity(t, component)]
        self.components_filter.remove(component)

    def filter_component(self, component):
        self.components_filter.remove(component)

    def filter_transaction(self, transaction):
        self.transactions_filter.remove(transaction)

    def filter_passing_transactions(self, spectra):
        self.transactions_filter = [t for t in self.transactions_filter
                                    if spectra.is_error(t)]

    def has_failing_transactions(self, spectra):
        for t in self.transactions_filter:
            if spectra.is_error(t):
                return True
        return False

    def keep_components(self, spectra, components):
        indexes = spectra.component_indexes(components)
        self.components_filter = [x for x in self.components_filter if x in indexes]

    def filter_ambiguity(self, spectra):
        to_filter = set()
        groups = set()
        for c in self.components_filter:
            activity = spectra.get_component_activity(c)
            if activity in groups:
                to_filter.add(c)
            else:
                groups.add(activity)
        self.components_filter = [x for x in self.components_filter if x not in to_filter]

    def print_filter(self, out=sys.stdout):
        out.write('Transactions:\t%s\n' % self.transactions_filter)
        out.write('Components:\t%s\n' % self.components_filter)

    def to_map(self):
        return {'transactions': self.transactions_filter[:], 'components': self.components_filter[:]}
