import os
import getpass
import shutil
import tempfile
import contextlib

def find_aseprite():
    possible_paths = []

    userName = getpass.getuser()

    if os.name == "nt":
        # Windows
        possible_paths = [
            r"C:\Program Files\Aseprite\Aseprite.exe",
            r"C:\Program Files (x86)\Aseprite\Aseprite.exe",
            r"C:\Program Files\Steam\steamapps\common\Aseprite\Aseprite.exe",
            r"C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe",
        ]
    elif os.name == "posix":
        # macOS or Linux
        possible_paths = [
            "/Applications/Aseprite.app/Contents/MacOS/aseprite",
            f"/Users/{userName}/Library/Application Support/Steam/steamapps/common/Aseprite/Aseprite.app/Contents/MacOS/aseprite",
            f"/Users/{userName}/.steam/debian-installation/steamapps/common/Aseprite/aseprite"
            "/usr/local/bin/aseprite",
            "/usr/bin/aseprite",
        ]
    else:
        # Unsupported OS
        return None

    for path in possible_paths:
        if os.path.isfile(path):
            print("Aseprite found at " + path)
            return path

    return None

@contextlib.contextmanager
def make_temp_directory():
    tempDirectory = tempfile.mkdtemp()
    try:
        yield tempDirectory
    finally:
        shutil.rmtree(tempDirectory)