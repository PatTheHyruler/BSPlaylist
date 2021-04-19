import platform
import os
import winreg
import ast
import json
import requests
import PySimpleGUI as sg
import threading
import hashlib


# global variables start
headers = {
    'authority': 'beatsaver.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'accept-language': 'en-US,en;q=0.9,et;q=0.8',
}
songsdict = {}
PlInfoMsgDict = {
    0: "Choose a playlist from the panel to the left",
    1: "Please only select 1 playlist"
}
# global variables end

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


steampath = get_steam_path()
path = get_game_path(steampath)
playlistspath = f"{path}Playlists"
songspath = f"{path}Beat Saber_Data\\CustomLevels"
# NB! need to make sure program works if path detection fails


class EmptyRequestError(Exception):
        def __init__(self, errors=""):
            super().__init__()
            self.errors = errors
            if bool(self.errors):
                print(f"Errors: {errors}")


class Playlist:
    def __init__(self, filepath):
        with open(filepath, encoding="utf8") as f:
            playlist = json.load(f)
        
        self.filepath = filepath
        self.deleted = False
        self.raw = playlist
        self.title = playlist["playlistTitle"]
        self.title_ext = self.title
        self.author = playlist["playlistAuthor"]
        try:
            self.description = playlist["playlistDescription"]
        except:
            self.description = ""

        global songsdict
        __initsongs = playlist["songs"]
        hashes = {}
        for song in __initsongs:
            songhash = song["hash"].lower()
            
            try:
                hashes[songhash] = {
                    "hash": songhash,
                    "songName": songsdict[songhash].name
                }
            except:
                print(filepath)
                print(songhash)

        self.songs = hashes
        
    def getData(self):
        namelist = []
        for song in self.songs:
            namelist.append(song["songName"])
        return namelist
    
    def getNames(self):
        self.getData()

    def remove(self, songhash):
        self.songs.pop(songhash)
        try:
            self.requestlist.pop(songhash)
        except:
            pass

    def save(self):
        print("saved")
        writedict = {}
        writedict["playlistTitle"] = self.title
        writedict["playlistAuthor"] = self.author
        if self.description:
            writedict["playlistDescription"] = self.description
        writedict["songs"] = []
        for song in self.songs:
            writedict["songs"].append({"hash": song})
        with open(self.filepath, "w") as f:
            json.dump(writedict, f)
            self.deleted = False
            pass

    def delete(self):
        if os.path.exists(self.filepath):
            os.remove(self.filepath)
            self.deleted = True

    def add(self, songhash):
        self.songs[songhash] = {"hash": songhash}
        self.save()


class Song():
    def __init__(self, songpath):
        with open(os.path.join(songpath, "info.dat"), "r", encoding="utf8") as f:
            info = json.load(f)
        self.name = info["_songName"]
        self.subname = info["_songSubName"]
        self.author = info["_levelAuthorName"]
        self.bpm = info["_beatsPerMinute"]
        songfilename = info["_songFilename"]
        coverimagefilename = info["_coverImageFilename"]
        self.diff_files = []
        for diff in info["_difficultyBeatmapSets"][0]["_difficultyBeatmaps"]:
            self.diff_files.append(os.path.join(songpath, diff["_beatmapFilename"]))
        files_to_hash = [item for item in self.diff_files]
        files_to_hash.insert(0, os.path.join(songpath, "Info.dat"))
        try:
            self.contributors = info["_customData"]["_contributors"]
        except:
            pass
        try:
            with open(os.path.join(songpath, "metadata.dat"), "r", encoding="utf8") as f:
                metadata = json.load(f)
            self.hash = metadata["hash"].lower()
        except:
            self.hash = sha1(files_to_hash).lower()
            print(self.hash)
    pass

    

def loadPlaylists(playlistspath):
    """This function just gets called by updatePlaylists()
    and shouldn't need to be used on its own."""
    playlists = []
    filenames = []
    for root, dirs, files in os.walk(playlistspath):
        for filename in files:
            #print(os.path.join(root, filename))
            playlistpath = os.path.join(root, filename)
            playlists.append(Playlist(playlistpath))
            filenames.append(filename)
    return playlists, filenames

def updatePlaylists(playlistspath):
    playlists, filenames = loadPlaylists(playlistspath)
    playlistnames = []
    for index, pl in enumerate(playlists):
        if pl.title not in playlistnames:
            playlistnames.append(pl.title)
        else:
            success = False
            for i in range(10):
                testname = f"{pl.title} - Copy {i+1}"
                if testname not in playlistnames:
                    playlistnames.append(testname)
                    pl.title_ext = testname
                    success = True
                    break
            if not success:
                playlistnames.append(filenames[index])
                pl.title_ext = filenames[index]

    playlistupdatelist = []
    for i in playlistnames:
        playlistupdatelist.append([i, "testtest"])

    #window.Element("-PLAYLISTS TABLE-").Update(values=playlistupdatelist)
    window["-PLAYLISTS TABLE-"].update(values=playlistupdatelist)

    # playlists - list of instances of Playlist class
    # filenames - list of filenames of playlists
    # playlistnames - list of modified playlist names (to deal with potential duplicate names)
    # all 3 lists ordered the same
    return playlists, filenames, playlistnames



def loadsongs(songspath):
    dirs = [os.path.join(songspath, item) for item in os.listdir(songspath) if os.path.isdir(os.path.join(songspath, item))]
    totalsongs = len(dirs)
    for counter, songdir in enumerate(dirs):
        songpath = os.path.join(songspath, songdir)
        #print(songpath)
        try:
            song = Song(songpath)
            songsdict[song.hash] = song
            #print(songsdict)
        except Exception as e:
            print(songpath)
            print(e)
        #print(f"\r{counter}/{totalsongs}")


playlisttable_headings = ["Playlist Name", "Header2"]
playlisttable_values = [["" for i in range(len(playlisttable_headings))]]
playlist_column = [
    [
        sg.Text("Playlists Folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
        sg.Button("Load/Reload Playlists", key="-RELOAD-")
    ],
    [
        sg.Table(
            values=playlisttable_values,
            headings=playlisttable_headings,
            enable_events=True,
            auto_size_columns=False,
            vertical_scroll_only=False,
            max_col_width=80,
            def_col_width=30,
            num_rows=20,
            justification='center',
            key="-PLAYLISTS TABLE-"
        ),
        sg.Button("Delete selected playlist(s)", key="-DELETE PLAYLISTS-")
    ],
]

song_list_text = [
    [sg.Text(text=PlInfoMsgDict[0],key="-PL INFOMSG-")]
]

songlisttable_headings = ["Song name", "add more columns later"]
songlisttable_values = [["" for i in range(len(songlisttable_headings))]]
song_list = [
    [
        sg.Table(
            values=songlisttable_values,
            headings=songlisttable_headings,
            enable_events=True,
            auto_size_columns=False,
            max_col_width=80,
            def_col_width=20,
            size=(40, 20),
            justification='center',
            key="-SONG TABLE-"
        )
    ]
]

layout1 = [
    [
        sg.Column(song_list_text),
    ]
]

layout2 = [
    [
        sg.Column(song_list, key="-SONG COLUMN-")
    ]
]

layout = [
    [
        sg.Column(playlist_column),
        sg.VSeparator(),
        sg.Column(layout1, key='-COL1-'),
        sg.Column(layout2, visible=False, key='-COL2-')
    ]
]

# Create the window
window = sg.Window("BS Playlist Editor", layout, finalize=True)

window["-FOLDER-"].update(playlistspath)


def updateNames(playlist):
    #print("updatenames")
    songupdatelist = []
    for i in playlist.getNames():
        songupdatelist.append([i, "placeholder"])
    window["-SONG TABLE-"].update(values=songupdatelist)

def setLayoutSonglist():
    window[f'-COL1-'].update(visible=False)
    window[f'-COL2-'].update(visible=True)
def resetLayout():
    window[f'-COL1-'].update(visible=True)
    window[f'-COL2-'].update(visible=False)
def updatePlInfoMsg(index, PlInfoMsgDict=PlInfoMsgDict):
    window["-PL INFOMSG-"].update(PlInfoMsgDict[index])
def resetUI():
    updatePlInfoMsg(0)
    resetLayout()

updatePlInfoMsg(0)

selectedsong = False

loadsongs(songspath)
loadPlaylists(playlistspath)
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    if event == "-PLAYLISTS TABLE-":
        selectedplaylists = values["-PLAYLISTS TABLE-"]
        if len(selectedplaylists) > 1:
            resetLayout()
            updatePlInfoMsg(1)
        elif len(selectedplaylists) == 1:
            setLayoutSonglist()
            currentplaylist = playlists[selectedplaylists[0]]
            updateNames(currentplaylist)
    
    if event == "-DELETE PLAYLISTS-":
        try:
            for index in selectedplaylists:
                playlists[index].delete()
        except:
            print("could not delete playlist")
            pass
        else:
            resetUI()
            updatePlaylists(playlistspath)
    
    if event == "-RELOAD-":
        resetUI()
        updatePlaylists(playlistspath)
        

window.close()

