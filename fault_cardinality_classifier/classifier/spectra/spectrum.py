import io
import sys
from .spectrum_filter import *

def process_component_name(name):
    delim = name.find('{')
    component_name = name[:delim]
    rng = tuple(map(int,name[delim+1:-1].split(',')))

    filename = name

    for d in ['#', '$']:
        delim = name.find(d)
        if delim != -1:
            filename = name[:delim]

    filename = 'src/main/java/' + filename.replace('.', '/') + '.java'

    return component_name, filename, rng

def process_component_tuple(component):
    return '{}{{{},{}}}'.format(component[0], str(component[2][0]), str(component[2][1]))

def div(a, b):
    return a / b if b != 0.0 else 0

def avg(lst):
    return div(sum(lst), len(lst))

class Spectrum:

    def __init__(self):
        self.matrix = []
        self.transactions = 0
        self.components = 0
        self.headers = []
        self.tests = []

    def read(self, stream):
        self.matrix = []

        self.headers = list(map(process_component_name, stream.readline().rstrip().split(';')[1:-1]))
        self.tests = []

        for line in stream:
            line = line.rstrip().split(';')
            self.tests.append(line[0])

            row = line[1:-1]
            row = list(map(int, row))

            if line[-1] == "pass":
                row.append(0) # pass
            else:
                row.append(1) # fail

            self.matrix.append(row)

        self.transactions = len(self.matrix)
        self.components = len(self.matrix[0]) - 1

    def read_file(self, filename):
        f = open(filename)
        self.read(f)
        f.close()

    def read_string(self, string):
        self.read(io.StringIO(string))

    def write(self, out):
        header = ';' + ';'.join(map(process_component_tuple, self.headers)) + ';outcome\n'
        out.write(header)
        for t, row in enumerate(self.matrix):
            line = self.tests[t] + ';' + ';'.join(map(str,row[:-1]))
            if row[-1] == 0:
                line = line + ';pass\n'
            else:
                line = line + ';fail\n'
            out.write(line)
        out.flush()

    def write_string(self):
        out = io.StringIO()
        self.write(out)
        return out.getvalue()

    def __repr__(self):
        return self.write_string()

    def write_file(self, filename):
        f = open(filename, 'w')
        self.write(f)
        f.close()

    def get_transaction_activity(self, transaction):
        return self.matrix[transaction]

    def get_activity(self, transaction, component):
        if component >= self.components or transaction > self.transactions:
            return 0
        return self.matrix[transaction][component]

    def is_error(self, transaction):
        return self.matrix[transaction][-1]

    def match_location(self, filename, line):
        ret = []
        for name, f, rng in self.headers:
            if line >= rng[0] and line <= rng[1] and filename.endswith(f):
                ret.append(name)
        return ret

    def match_name(self, name):
        for n, _, _ in self.headers:
            if n == name:
                return True
        return False

    def component_indexes(self, comps):
        return [c for c in range(self.components) if self.headers[c][0] in comps]

    def has_failing_transactions(self, spectrum_filter=None):
        if not spectrum_filter:
            spectrum_filter = SpectrumFilter(self)

        return spectrum_filter.has_failing_transactions(self)

    def get_failing_transactions_coverage(self, spectrum_filter=None):
        if not spectrum_filter:
            spectrum_filter = SpectrumFilter(self)

        res = []
        for t in spectrum_filter.transactions_filter:
            if self.is_error(t):
                act = self.matrix[t][:-1]
                res.append(sum(act) / len(act))
        return avg(res)


    def get_failing_tests(self, spectrum_filter=None):
        if not spectrum_filter:
            spectrum_filter = SpectrumFilter(self)

        ret = []
        for t in spectrum_filter.transactions_filter:
            if self.is_error(t):
                ret.append(self.tests[t])
        return ret

    def get_tests(self, spectrum_filter=None):
        if not spectrum_filter:
            spectrum_filter = SpectrumFilter(self)

        ret = []
        for t in spectrum_filter.transactions_filter:
            ret.append(self.tests[t])
        return ret

    def set_failing_tests(self, failing_tests, spectrum_filter=None):
        if not spectrum_filter:
            spectrum_filter = SpectrumFilter(self)

        for t in spectrum_filter.transactions_filter:
            if self.tests[t] in failing_tests:
                self.matrix[t][-1] = 1
            else:
                self.matrix[t][-1] = 0

    def set_errors(self, error_transactions):
        for t in error_transactions:
            self.matrix[t][-1] = 1

    def get_component_activity(self, component):
        ret = str()
        for transaction in self.matrix:
            ret += str(transaction[component])
        return ret

    def contains_tests(self, tests):
        own_tests = self.get_tests()
        for test in tests:
            if not test in own_tests:
                return False
        return True

    def print_spectrum(self, out=sys.stdout, spectrum_filter=None):
        if not spectrum_filter:
            spectrum_filter = SpectrumFilter(self)

        out.write('Tests:\n')
        for t in spectrum_filter.transactions_filter:
            out.write('{} - {}\n'.format(str(t), self.tests[t]))

        out.write('\nComponents:\n')
        for c in spectrum_filter.components_filter:
            out.write('{} - {}\n'.format(str(c), self.headers[c][0]))

        out.write('\nMatrix:\n')
        for t in spectrum_filter.transactions_filter:

            for c in spectrum_filter.components_filter:
                out.write('%d ' % self.get_activity(t, c))

            if self.is_error(t):
                out.write('x\n')
            else:
                out.write('.\n')
