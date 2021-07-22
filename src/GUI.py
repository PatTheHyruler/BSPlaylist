from src.GUIutils import *
from src.funcs import updateplaylists, clear
import PySimpleGUI as sg
from src.utils import WindowClosedError
from copy import deepcopy
import os
from src.beatsaver import BeatSaver
from src.bsr import Bsr


def gui_loop(window, playlists, playlistspath, songsdict, selectedplaylists):
    event, values = window.read()
    filenames = playlistnames = []
    if event == "Exit" or event == sg.WIN_CLOSED:
        raise WindowClosedError
    if event == "-PLAYLISTS TABLE-":
        selectedplaylists = values["-PLAYLISTS TABLE-"]
        if len(selectedplaylists) > 1:
            reset_layout(window)
            update_pl_info_msg(window, 1)
        elif len(selectedplaylists) == 1:
            set_layout_song_list(window)
            currentplaylist = playlists[selectedplaylists[0]]
            update_names(window, currentplaylist)
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
            reset_ui(window)
            playlists, filenames, playlistnames = updateplaylists(playlistspath, window, songsdict)
    
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
                        playlists, filenames, playlistnames = updateplaylists(playlistspath, window, songsdict)
                        reset_ui(window)
                        break
                del newplaylist, filepath_base, filepath
        except:
            print("could not duplicate playlist")
            pass

    if event == "-ADD BSR-":
        currentplaylists = [playlists[index] for index in selectedplaylists]
        bsrlist = Bsr.interpret(values["-ADD BSR INPUT-"])
        hashlist = [songhash for songhash in [BeatSaver.get_hash_by_key(bsr) for bsr in bsrlist]
                    if songhash is not None]
        if len(hashlist) > 0:
            for playlist in currentplaylists:
                playlist.add_multiple(hashlist, songsdict)
            reset_ui(window)
            clear(playlists, filenames, playlistnames)
            playlists, filenames, playlistnames = updateplaylists(playlistspath, window, songsdict)
        else:
            sg.popup_ok("No compatible bsr key in textbox!", title="ERROR!")

    if event == "-RELOAD-":
        reset_ui(window)
        clear(playlists, filenames, playlistnames)
        playlists, filenames, playlistnames = updateplaylists(playlistspath, window, songsdict)

    return selectedplaylists, playlists
