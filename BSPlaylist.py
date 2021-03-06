import PySimpleGUI as sg
from src.utils import get_game_path, get_steam_path, WindowClosedError
from src.funcs import updateplaylists, loadsongs
from src.GUI import gui_loop
from src.GUIutils import *

import asyncio

# global variables start
songsdict = {}


steampath = get_steam_path()
path = None
if steampath is not None:
    try:
        path = get_game_path(steampath)
    except:
        pass

if path is None:
    path = sg.popup_get_folder("Please provide your Beat Saber folder path",
                               title="Couldn't locate Beat Saber folder")

if path is not None:
    playlistspath = f"{path}Playlists"
    songspath = f"{path}Beat Saber_Data\\CustomLevels"
else:
    playlistspath = sg.popup_get_folder(
        "Please provide your playlists folder path",
        title="No Beat Saber folder"
    )
    songspath = sg.popup_get_folder(
        "Please provide your custom songs folder path",
        title="No Beat Saber folder"
    )

if playlistspath is None:
    quit("no playlistspath")
elif songspath is None:
    quit("no songspath")

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
    ],
]
playlist_actions_column = [
    [
        sg.Button("Delete selected playlist(s)", key="-DELETE PLAYLISTS-")
    ],
    [
        sg.Button("Duplicate selected playlist", key="-DUPLICATE PLAYLISTS-")
    ],
    [
        sg.Input("", tooltip="add bsr code here", size=(13, 10), key="-ADD BSR INPUT-"),
        sg.Button("Add bsr", key="-ADD BSR-")
    ]
]

song_list_text = [
    [sg.Text(text=PlInfoMsgDict[str(0)], key="-PL INFOMSG-")]
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

songlist_actions_column = [
    [
        sg.Button("Remove selected song(s) from playlist", key="-REMOVE SONGS-")
    ],
    [
        sg.Button("Delete selected song(s) from disk", key="-DELETE SONGS-")
    ]
]

layout1 = [
    [
        sg.Column(song_list_text),
    ]
]

layout2 = [
    [
        sg.Column(song_list, key="-SONG COLUMN-"),
        sg.Column(songlist_actions_column)
    ]
]

layout = [
    [
        sg.Column(playlist_column),
        sg.Column(playlist_actions_column),
        sg.VSeparator(),
        sg.Column(layout1, key='-COL1-'),
        sg.Column(layout2, visible=False, key='-COL2-')
    ]
]

# Create the window
window = sg.Window("BS Playlist Editor", layout, finalize=True)

window["-FOLDER-"].update(playlistspath)

update_pl_info_msg(window, 0)

selectedsong = False

loadsongs(songspath, songsdict)
playlists, filenames, playlistnames = updateplaylists(playlistspath, window, songsdict)

selectedplaylists = []
selectedsongs = []
playlist_songs = []


async def run(window, playlists, playlistspath, songsdict, selectedplaylists, selectedsongs, playlist_songs):
    while True:
        try:
            print(f"selectedplaylists: {selectedplaylists}")
            # print(f"playlists: {[playlist.title for playlist in playlists]}")
            selectedplaylists, playlists, selectedsongs, playlist_songs = await gui_loop(window, playlists, playlistspath, songsdict, selectedplaylists, selectedsongs, playlist_songs)
        except WindowClosedError:
            break


loop = asyncio.get_event_loop()
loop.run_until_complete(run(window, playlists, playlistspath, songsdict, selectedplaylists, selectedsongs, playlist_songs))
loop.close()

window.close()
