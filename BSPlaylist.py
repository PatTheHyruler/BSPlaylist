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
        
    def getNames(self):
        namelist = []
        for songhash in self.songs:
            song = self.songs[songhash]
            try:
                namelist.append(song["songName"])
            except KeyError:
                namelist.append("[Requesting song info from Beatsaver...]")
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


    

def loadPlaylists(playlistspath):
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


def queueToTop(playlistname_ext):
    try:
        queueprioritylist.insert(0, queueprioritylist.pop(queueprioritylist.index(playlistname_ext)))
    except ValueError:
        queueprioritylist.append(playlistname_ext)
        queueprioritylist.insert(0, queueprioritylist.pop(queueprioritylist.index(playlistname_ext)))

def queuefunc(currentqueue, queue: dict, playlist: object):
    songhash = playlist.requestlist.pop(0)
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
        sg.Button("Delete selected playlist", key="-deleteplaylistbutton-")
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
            size=(40, 20),
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

if playlistspath:
    playlists, filenames, playlistnames = updatePlaylists(playlistspath)

def runQueue(queueactive):
    while queueactive:
        try:
            queuetop = queueprioritylist[0]
            currentqueue = queue[queuetop]
            queueplaylist = playlists[playlistnames.index(queueprioritylist[0])]
        except Exception:
            pass
            #print(e)
        try:
            queuefunc(currentqueue, queue, queueplaylist)
            print("runqueue")
        except IndexError:
            queueactive = False
        except Exception:
            #raise
            #print(e)
            pass

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
while True:
    threading.Thread(target=runQueue, args = (queueactive,), daemon=True).start()

    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    if event == "-PLAYLISTS TABLE-":
        selectedplaylistindex = values["-PLAYLISTS TABLE-"]
        if len(selectedplaylistindex) == 1:
            setLayoutSonglist()
        if len(selectedplaylistindex) > 1:
            updatePlInfoMsg(1)

        print(values["-PLAYLISTS TABLE-"])
        

window.close()

