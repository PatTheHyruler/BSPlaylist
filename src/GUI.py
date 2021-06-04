from src.GUIutils import *
from src.funcs import updatePlaylists
import PySimpleGUI as sg
from src.utils import WindowClosedError
from copy import deepcopy
import os

def GUIloop(window,playlists,playlistspath,songsdict,selectedplaylists):
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        raise WindowClosedError
    if event == "-PLAYLISTS TABLE-":
        selectedplaylists = values["-PLAYLISTS TABLE-"]
        if len(selectedplaylists) > 1:
            resetLayout(window)
            updatePlInfoMsg(window,1)
        elif len(selectedplaylists) == 1:
            setLayoutSonglist(window)
            currentplaylist = playlists[selectedplaylists[0]]
            updateNames(window,currentplaylist)

    if event == "-DELETE PLAYLISTS-":
        try:
            for index in selectedplaylists:
                playlists[index].delete()
        except:
            print("could not delete playlist")
            pass
        else:
            # Currently the program reloads playlists and UI when a playlist is deleted.
            # However, functionality could be added where the refresh isn't automatic,
            # and thus a "deleted" playlist would still be stored in memory.
            resetUI(window)
            playlists, filenames, playlistnames = updatePlaylists(playlistspath, window, songsdict)
    
    if event == "-DUPLICATE PLAYLISTS-":
        try:
            if len(selectedplaylists) == 1:
                newplaylist = deepcopy(playlists[selectedplaylists[0]])
                filepath_base = newplaylist.filepath
                success = False
                for i in range(10):
                    filepath = filepath_base + f" - Copy {i}"
                    if not os.path.exists(filepath):
                        newplaylist.filepath = filepath
                        newplaylist.save()
                        success = True
                    if success:
                        playlists, filenames, playlistnames = updatePlaylists(playlistspath, window, songsdict)
                        resetUI(window)
                        break
                del newplaylist, filepath_base, filepath
        except:
            print("could not duplicate playlist")
            pass
    
    if event == "-RELOAD-":
        resetUI(window)
        playlists, filenames, playlistnames = updatePlaylists(playlistspath, window, songsdict)
    
    return selectedplaylists