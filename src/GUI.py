from src.GUIutils import *
from src.funcs import updatePlaylists, clear
import PySimpleGUI as sg
from src.utils import WindowClosedError
from copy import deepcopy
import os
from src.beatsaver import BeatSaver
from src.bsr import Bsr

def GUIloop(window,playlists,playlistspath,songsdict,selectedplaylists):
    event, values = window.read()
    filenames = playlistnames = []
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
            updateNames(window, currentplaylist)
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
            clear(playlists, filenames, playlistnames)
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
                        clear(playlists, filenames, playlistnames)
                        playlists, filenames, playlistnames = updatePlaylists(playlistspath, window, songsdict)
                        resetUI(window)
                        break
                del newplaylist, filepath_base, filepath
        except:
            print("could not duplicate playlist")
            pass

    if event == "-ADD BSR-":
        currentplaylists = [playlists[index] for index in selectedplaylists]
        bsrlist = Bsr.interpret(values["-ADD BSR INPUT-"])
        hashlist = [hash for hash in [BeatSaver.get_hash_by_key(bsr) for bsr in bsrlist] if hash is not None]
        if len(hashlist) > 0:
            for playlist in currentplaylists:
                playlist.add_multiple(hashlist, songsdict)
            resetUI(window)
            clear(playlists, filenames, playlistnames)
            playlists, filenames, playlistnames = updatePlaylists(playlistspath, window, songsdict)
        else:
            sg.popup_ok("No compatible bsr key in textbox!", title="ERROR!")

    if event == "-RELOAD-":
        resetUI(window)
        clear(playlists, filenames, playlistnames)
        playlists, filenames, playlistnames = updatePlaylists(playlistspath, window, songsdict)

    return selectedplaylists, playlists