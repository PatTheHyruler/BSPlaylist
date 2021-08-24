import os
from typing import List

from src.playlist import Playlist
from src.song import Song


def loadplaylists(playlistspath, songsdict):
    """This function just gets called by updateplaylists()
    and shouldn't need to be used on its own."""
    playlists = []
    filenames = []
    playlistfiles = [os.path.join(playlistspath, item) for item in os.listdir(playlistspath)
                     if os.path.isfile(os.path.join(playlistspath, item))]
    for filename in playlistfiles:
        playlistpath = os.path.join(playlistspath, filename)
        playlists.append(Playlist(playlistpath, songsdict))
        filenames.append(filename)
    return playlists, filenames


def updateplaylists(playlistspath, window, songsdict):
    playlists, filenames = loadplaylists(playlistspath, songsdict)
    print(playlists[0].title)
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

    # window.Element("-PLAYLISTS TABLE-").Update(values=playlistupdatelist)
    window["-PLAYLISTS TABLE-"].update(values=playlistupdatelist)

    # playlists - list of instances of Playlist class
    # filenames - list of filenames of playlists
    # playlistnames - list of modified playlist names (to deal with potential duplicate names)
    # all 3 lists ordered the same
    return playlists, filenames, playlistnames


def get_playlist_songs(playlist: Playlist, window, songsdict) -> List[Song]:
    songslist = []
    for songhash in playlist.songs:
        song = songsdict[songhash]
        songslist.append(song)
    window["-SONG TABLE-"].update(values=[song.name for song in songslist])
    return songslist


def clear(*args):
    for arg in args:
        del arg


def loadsongs(songspath, songsdict):
    dirs = [os.path.join(songspath, item) for item in os.listdir(songspath)
            if os.path.isdir(os.path.join(songspath, item))]
    totalsongs = len(dirs)
    for counter, songdir in enumerate(dirs):
        songpath = os.path.join(songspath, songdir)
        try:
            song = Song(songpath)
            songsdict[song.hash] = song
        except Exception as e:
            print(songpath)
            print(e)
