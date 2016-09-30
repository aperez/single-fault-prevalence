import argparse
import shutil
import uuid
import classifier
import glob2
import os

PLUGIN_URL = "https://github.com/aperez/aes-maven-plugin.git"

def install_maven_plugin():
    gr = classifier.GitRepo()
    gr.clone(PLUGIN_URL, extra_args='-b single-fault-prevalence --single-branch')
    mc = classifier.MavenClient(gr.get_folder())
    mc.install()
    gr.remove()
    print("Maven plugin is installed.")
    print("Run it using the command 'mvn pt.up.fe.aes:aes-maven-plugin:1.1-SNAPSHOT:test'.")

def compare_commits(url, commit_sets):
    mhs = classifier.MHS()
    gr = classifier.GitRepo()
    gr.clone(url)

    for faulty, fix in commit_sets:
        gr.checkout(fix)
        diff = gr.diff(faulty)

        # run tests in fixed version
        mc = classifier.MavenClient(gr.get_folder())
        mc.test_compile(clean=True)
        mc.run_command('pt.up.fe.aes:aes-maven-plugin:1.1-SNAPSHOT:test')

        spectra = {}
        temp_folders = []
        for target_location in glob2.glob(gr.get_folder() + "/**/target/"):
            spectrum_location = target_location + 'aes-report/spectrum.csv'
            test_classes_location = target_location + 'test-classes/'

            # temp folder for compiled test cases
            if os.path.isdir(test_classes_location):
                temp_folder = classifier.TempFolder.create(test_classes_location)
                temp_folders.append(temp_folder)

            if os.path.isfile(spectrum_location):
                spectrum_fixed = classifier.Spectrum()
                spectrum_fixed.read_file(spectrum_location)
                spectra[spectrum_location] = spectrum_fixed
                # print("Fixed version spectrum:")
                # spectrum_fixed.print_spectrum()

        if len(spectra) == 0 or len(temp_folders) == 0: continue

        gr.checkout(faulty)
        mc.compile(clean=True)
        for temp_folder in temp_folders:
            temp_folder.restore()
        ret = mc.run_command('pt.up.fe.aes:aes-maven-plugin:1.1-SNAPSHOT:test')

        if ret != 0: continue # skip analysis if there are compilation/runtime errors

        spectrum_faulty = None

        for location, spectrum_fixed in spectra.items():
            if os.path.isfile(location):
                spectrum = classifier.Spectrum()
                spectrum.read_file(location)
                if spectrum.has_failing_transactions():
                    spectrum_faulty = spectrum
                    # print("\n\nFaulty version spectrum:")
                    # spectrum_faulty.print_spectrum()
                    break

        if spectrum_faulty == None: continue

        # create a filter for the fixed version's spectrum
        sf = classifier.SpectrumFilter(spectrum_fixed)

        # keep modified components according to diff between faulty and fix
        modified = classifier.get_modified_components(diff, spectrum_faulty, spectrum_fixed)
        sf.keep_components(spectrum_fixed, modified)

        # filter tests that do not fail in faulty version
        tests = spectrum_faulty.get_failing_tests()
        spectrum_fixed.set_failing_tests(tests)
        sf.filter_passing_transactions(spectrum_fixed)

        # filter global ambiguity groups
        sf.filter_ambiguity(spectrum_fixed)

        print("\n\nFiltered spectrum:")
        spectrum_fixed.print_spectrum(spectrum_filter=sf)

        trie = mhs.calculate(spectrum_fixed, spectrum_filter=sf)
        hitting_sets = list(trie)
        print("Minimal hitting sets: ", list(trie))

        classification = str()
        if len(hitting_sets) == 0:
            classification = "not-a-fix"
        elif len(hitting_sets) == 1 and len(hitting_sets[0]) == 1:
            classification = "single-fault"
        else:
            classification = "multiple-fault"
        print("Commit pair ({}, {}) has classification: {}.".format(faulty, fix, classification))
    gr.remove()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Classify fault cardinality between two commits.')
    parser.add_argument('-i', '--install-plugin', action='store_true', help='Install maven plugin.')
    args = parser.parse_args()

    if args.install_plugin:
        install_maven_plugin()
