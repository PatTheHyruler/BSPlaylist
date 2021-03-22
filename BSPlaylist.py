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
# global variables end


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
            try:
                hashes[song["hash"]] = {"hash": song["hash"], "name": song["songName"]}
            except KeyError:
                hashes[song["hash"]] = {"hash": song["hash"]}
                requestlist.append(song["hash"])
        self.songs = hashes
        self.requestlist = requestlist
        
    def getNames(self):
        namelist = []
        for songhash in self.songs:
            song = self.songs[songhash]
            try:
                namelist.append(song["name"])
            except KeyError:
                namelist.append("[Requesting song info from Beatsaver...]")
        return namelist

    def addtoqueue(self, queue):
        print(self.requestlist)
        queue[self.title_ext] = self.requestlist
        return queue


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
                testname = f"{pl.title} - Copy {i}"
                if testname not in playlistnames:
                    playlistnames.append(testname)
                    pl.title_ext = testname
                    success = True
                    break
            if not success:
                playlistnames.append(filenames[index])
                pl.title_ext = filenames[index]
                
    window["-FILE LIST-"].update(playlistnames)
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
    playlist.songs[songhash]["name"] = songdata["metadata"]["songName"]
    print("Loaded "+songdata["metadata"]["songName"])






playlist_column = [
    [
        sg.Text("Playlists Folder"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
        sg.Button("Load/Reload Playlists", key="-RELOAD-")
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-FILE LIST-"
        )
    ],
]

song_list_text = [
    [sg.Text("Choose a playlist from the panel to the left")]
]

song_list = [
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-SONG LIST-"
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
        sg.Column(song_list),
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

layout = 1

def runQueue():
    print("runqueue")
    try:
        queuetop = queueprioritylist[0]
        currentqueue = queue[queuetop]
        queueplaylist = playlists[playlistnames.index(queueprioritylist[0])]
    except Exception as e:
        pass
        #print(e)
    try:
        queuefunc(currentqueue, queue, queueplaylist)
    except Exception as e:
        pass
        #print(e)

def updateNames(playlist):
    print("updatenames")
    window["-SONG LIST-"].update(playlist.getNames())

while True:
    threading.Thread(target=runQueue, daemon=True).start()
    
    print(threading.active_count())

    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    if event == "-FOLDER-":
        playlistspath = values["-FOLDER-"]
    if event == "-RELOAD-":
        playlists, filenames, playlistnames = updatePlaylists(playlistspath)
    if event == "-FILE LIST-":  # A file was chosen from the listbox
        print(f"Layout: {layout}")
        print(values["-FILE LIST-"])
        if layout == 1:
            window[f'-COL{layout}-'].update(visible=False)
            layout = 2
            window[f'-COL{layout}-'].update(visible=True)
        
        
        currentplaylistname = values["-FILE LIST-"][0]
        # playlistindex - currently selected playlist's index
        playlistindex = playlistnames.index(currentplaylistname)
        # playlist = currently selected playlist
        playlist = playlists[playlistindex]
        
        queueToTop(currentplaylistname)
        queue = playlist.addtoqueue(queue)
        print("Queue:")
        print(queue)
        
        #print(playlist.songs)
        
        
    
    if layout == 2:
        threading.Thread(target=updateNames, daemon=True, args = (playlist,)).start()
        

window.close()

