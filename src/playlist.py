import json
import os


class Playlist:
    def __init__(self, filepath, songsdict):
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
        self.songs = {}

        __initsongs = playlist["songs"]
        for song in __initsongs:
            songhash = song["hash"].lower()

            self._initsong(songhash, songsdict)

    def _initsong(self, songhash, songsdict):
        try:
            self.songs[songhash] = {
                "hash": songhash,
                "songName": songsdict[songhash].name
            }
        except:
            self.songs[songhash] = {
                "hash": songhash,
                "songName": "NOT DOWNLOADED"
            }

    def get_data(self):
        namelist = []
        for songhash in self.songs:
            namelist.append(self.songs[songhash]["songName"])
        return namelist
    
    def get_names(self):
        return self.get_data()

    def remove(self, songhash):
        self.songs.pop(songhash)

    def save(self):
        print("saved")
        writedict = {
            "playlistTitle": self.title,
            "playlistAuthor": self.author
        }
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

    def add(self, songhash, songsdict):
        if songhash in self.songs:
            return
        self._initsong(songhash, songsdict)
        self.save()

    def add_multiple(self, songhash_list, songsdict):
        for songhash in songhash_list:
            self.add(songhash, songsdict)
