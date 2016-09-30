import uuid
import shutil

class TempFolder(object):
    def __init__(self, folder, temp):
        self.folder = folder
        self.temp = temp
        shutil.copytree(self.folder, self.temp)

    def restore(self, destroy=True):
        shutil.copytree(self.temp, self.folder)
        if destroy:
            self.destroy()

    def destroy(self):
        shutil.rmtree(self.temp, ignore_errors=True)

    @classmethod
    def create(cls, folder):
        return cls(folder, str(uuid.uuid4()))
