from src.GUIutils import *
from src.funcs import updatePlaylists
import PySimpleGUI as sg
from src.utils import WindowClosedError

def GUIloop(window,playlists,playlistspath,songsdict):
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        raise WindowClosedError
    if event == "-PLAYLISTS TABLE-":
        selectedplaylists = values["-PLAYLISTS TABLE-"]
        if len(selectedplaylists) > 1:
            resetLayout()
            updatePlInfoMsg(1)
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
            resetUI()
            playlists, filenames, playlistnames = updatePlaylists(playlistspath, window, songsdict)
    
    if event == "-RELOAD-":
        resetUI(window)
        playlists, filenames, playlistnames = updatePlaylists(playlistspath, window, songsdict)