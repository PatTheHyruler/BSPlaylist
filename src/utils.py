import hashlib
import platform
import winreg
import os
import ast

def sha1(fnames):
    hash_sha1 = hashlib.sha1()
    for fname in fnames:
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha1.update(chunk)
    return hash_sha1.hexdigest()

def get_steam_path():
    
    if platform.system() == "Windows":
        """Get Steam install location from the Windows registry"""
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                "SOFTWARE\\WOW6432Node\\Valve\\Steam")
            value = winreg.QueryValueEx(key, "InstallPath")[0]
            return value
        except:
            print("Couldn't locate Steam.")
    elif platform.system() == "Linux":
        print("Automatic Steam location detection not supported on Linux, sorry.")

def get_game_path(steampath):
    """Scan through every Steam library and try to find a Beat Saber installation"""
    try:
        gamepaths = [f"{steampath}"]
        with open(f"{steampath}\\steamapps\\libraryfolders.vdf", "r") as f:
            for l in f:
                # If is an absolute path with a drive letter (eg "D:\\Games")
                if ":\\\\" in l:
                    gamepaths.append(ast.literal_eval("\""+l.split("\t")[-1][1:-2]+"\""))
        for gamepath in gamepaths:
            if (os.path.isfile(f"{gamepath}\\steamapps\\appmanifest_620980.acf")):
                return f"{gamepath}\\steamapps\\common\\Beat Saber\\"
        raise Exception("Couldn't locate Beat Saber")
    except:
        print("Couldn't locate Beat Saber.")

class WindowClosedError(Exception):
    """Raised when program window is closed"""
    pass