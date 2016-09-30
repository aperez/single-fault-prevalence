import os
import glob2
import classifier

class CommitSpectra(object):
    def __init__(self, gr, commit):
        self.commit = commit
        self.gr = gr
        self.mc = classifier.MavenClient(self.gr.get_folder())

        self.spectra = {}
        self.temp_folders = []

        self.checkout()
        self.mc.test_compile(clean=True)
        ret = self.mc.run_command('pt.up.fe.aes:aes-maven-plugin:1.1-SNAPSHOT:test')

        if ret == 0:
            for target_location in glob2.glob(self.gr.get_folder() + "/**/target/"):
                spectrum_location = target_location + 'aes-report/spectrum.csv'
                test_classes_location = target_location + 'test-classes/'

                if os.path.isdir(test_classes_location):
                    temp_folder = classifier.TempFolder.create(test_classes_location)
                    self.temp_folders.append(temp_folder)

                if os.path.isfile(spectrum_location):
                    spectrum = classifier.Spectrum()
                    spectrum.read_file(spectrum_location)
                    self.spectra[spectrum_location] = spectrum

    def checkout(self):
        self.gr.checkout(self.commit)

    def compile(self):
        self.mc.compile(clean=True)

    def get_failing_spectrum(self, fixed_spectra):
        ret = self.mc.run_command('pt.up.fe.aes:aes-maven-plugin:1.1-SNAPSHOT:test')
        if ret == 0:
            for location, spectrum_fixed in fixed_spectra.items():
                if os.path.isfile(location):
                    spectrum = classifier.Spectrum()
                    spectrum.read_file(location)
                    if spectrum.has_failing_transactions():
                        return (spectrum, spectrum_fixed, location)
        return None

    def is_valid(self):
        return len(self.spectra) != 0 and len(self.temp_folders) != 0

    def has_failing_transactions(self):
        for _, spectrum in self.spectra.items():
            if spectrum.has_failing_transactions():
                return True
        return False

    def is_passing(self):
        return self.is_valid() and not self.has_failing_transactions()

    def diff(self, commit):
        self.gr.checkout(self.commit)
        return self.gr.diff(commit)

    def restore_tests(self):
        for temp_folder in self.temp_folders:
            temp_folder.restore(destroy=False)

    def destroy(self):
        for temp_folder in self.temp_folders:
            temp_folder.destroy()

    def __del__(self):
        self.destroy()

    def store(self, collection):
        spectra = {}
        for path, s in self.spectra.items():
            spectra[path] = str(s)

        obj = {'sha1': str(self.commit),
               'author': str(self.commit.author),
               'message': self.commit.message,
               'parents': list(map(str, self.commit.parents)),
               'date': self.commit.committed_date,
               'spectra': spectra}
        collection.store(obj)

    def contains_tests(self, location, tests):
        if location in self.spectra:
            spectrum = self.spectra[location]
            return spectrum.contains_tests(tests)

        return False
