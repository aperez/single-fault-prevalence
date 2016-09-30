import classifier.process as process

class MavenClient(object):
    def __init__(self, folder):
        self.folder = folder

    def get_folder(self):
        return self.folder

    def command(cmd):
        def func(self, clean=False):
            mvn = 'mvn'
            if clean:
                mvn = mvn + ' clean'
            ret = process.call('{} {}'.format(mvn, cmd), cwd=self.folder)
            return ret
        return func

    def run_command(self, cmd, clean=False):
        return self.__class__.command(cmd)(self, clean)

    compile = command("compile")
    install = command("install")
    test = command("test")
    test_compile = command("test-compile")
