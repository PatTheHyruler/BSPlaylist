import platform
import os
import winreg
import ast
import json
import requests
import PySimpleGUI as sg
import threading


# global variables start
headers = {
    'authority': 'beatsaver.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'accept-language': 'en-US,en;q=0.9,et;q=0.8',
}
queue = {}
queueprioritylist = []
queueactive = False
# global variables end
PlInfoMsgDict = {
    0: "Choose a playlist from the panel to the left",
    1: "Please only select 1 playlist"
}
songsdict = {}

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
        
        __initsongs = playlist["songs"]
        hashes = {}
        requestlist = []
        for song in __initsongs:
            hashes[song["hash"]] = {"hash": song["hash"]}
            requestlist.append(song["hash"])
        self.songs = hashes
        self.requestlist = requestlist
        #global queueactive
        #queueactive = True
        
    def getNames(self):
        namelist = []
        for songhash in self.songs:
            song = self.songs[songhash]
            try:
                namelist.append(song["songName"])
            except KeyError:
                namelist.append("[Getting song info...]")
        return namelist

    def addtoqueue(self, queue):
        queue[self.title_ext] = self.requestlist
        return queue

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
        with open(os.path.join(songpath, "metadata.dat"), "r", encoding="utf8") as f:
            metadata = json.load(f)
        self.hash = metadata["hash"]
        with open(os.path.join(songpath, "info.dat"), "r", encoding="utf8") as f:
            info = json.load(f)
        self.name = info["_songName"]
        self.subname = info["_songSubName"]
        self.author = info["_levelAuthorName"]
        self.bpm = info["_beatsPerMinute"]
        songfilename = info["_songFilename"]
        coverimagefilename = info["_coverImageFilename"]
        try:
            self.contributors = info["_customData"]["_contributors"]
        except:
            pass
        
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
        global queue
        pl.addtoqueue(queue)

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


def queueToTop(playlistname_ext):
    global queueprioritylist
    try:
        queueprioritylist.insert(0, queueprioritylist.pop(queueprioritylist.index(playlistname_ext)))
    except ValueError:
        queueprioritylist.append(playlistname_ext)
        queueprioritylist.insert(0, queueprioritylist.pop(queueprioritylist.index(playlistname_ext)))

def queuefunc(currentqueue, queue: dict, playlist: object):
    try:
        songhash = playlist.requestlist.pop(0)
    except IndexError:
        raise EmptyRequestError()
    url = f"https://beatsaver.com/api/maps/by-hash/{songhash}"
    text = requests.get(url, headers=headers).text
    songdata = json.loads(text)
    playlist.songs[songhash]["songName"] = songdata["metadata"]["songName"]
    playlist.songs[songhash]["downloadURL"] = songdata["downloadURL"]
    playlist.songs[songhash]["key"] = songdata["key"]
    playlist.songs[songhash]["coverURL"] = songdata["coverURL"]

    print("Loaded "+songdata["metadata"]["songName"])
    try:
        if currentplaylist == playlist:
            updateNames(playlist)
    except:
        pass

def loadsongs(songspath):
    for root, dirs, files in os.walk(songspath):
        for filename in files:
            #print(os.path.join(root, filename))
            songpath = os.path.join(root, filename)
            song = Song(songpath)
            songsdict[song.hash] = song
            print(songsdict)
            
loadsongs(songspath)


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

print(f"before init {queueactive}")
if playlistspath:
    playlists, filenames, playlistnames = updatePlaylists(playlistspath)
print(f"after init {queueactive}")

def runQueue():
    global queueactive
    global queueprioritylist
    while True:
        if queueactive:
            if not bool(queue):
                queueactive = False
            print(f"queue: {queue}")
            print(f"queueactive: {queueactive}\nqueueprioritylist: {queueprioritylist}")
            try:
                queuetop = queueprioritylist[0]
                currentqueue = queue[queuetop]
                queueplaylist = playlists[playlistnames.index(queueprioritylist[0])]
            except Exception:
                #raise
                pass
                #print(e)
            try:
                queuefunc(currentqueue, queue, queueplaylist)
            except EmptyRequestError:
                #raise
                if bool(queueprioritylist):
                    queueprioritylist.pop(0)
                if bool(queue):
                    queue.pop(queuetop)
            except Exception as e:
                #raise
                print(e)
                pass
            if len(queueprioritylist) == 0:
                if bool(queue):
                    print("got here")
                    for key in queue:
                        queueToTop(key)
                        break


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
threading.Thread(target=runQueue, daemon=True).start()
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
            queueactive = True
            setLayoutSonglist()
            currentplaylist = playlists[selectedplaylists[0]]
            updateNames(currentplaylist)
            queueToTop(playlistnames[selectedplaylists[0]])
    
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

