import json
import os
import requests
import PySimpleGUI as sg
from src.utils import get_game_path, get_steam_path, WindowClosedError
from src.funcs import updatePlaylists, loadsongs
from src.playlist import Playlist
from src.song import Song
from src.GUI import GUIloop
from src.GUIutils import *

# global variables start
headers = {
    'authority': 'beatsaver.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'accept-language': 'en-US,en;q=0.9,et;q=0.8',
}
songsdict = {}


steampath = get_steam_path()
path = get_game_path(steampath)
playlistspath = f"{path}Playlists"
songspath = f"{path}Beat Saber_Data\\CustomLevels"
# NB! need to make sure program works if path detection fails




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
    [sg.Text(text=PlInfoMsgDict[str(0)],key="-PL INFOMSG-")]
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




updatePlInfoMsg(window,0)

selectedsong = False

loadsongs(songspath, songsdict)
playlists, filenames, playlistnames = updatePlaylists(playlistspath, window, songsdict)
while True:
    try:
        GUIloop(window,playlists,playlistspath,songsdict)
    except WindowClosedError:
        break

window.close()

