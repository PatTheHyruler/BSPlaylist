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

        __initsongs = playlist["songs"]
        hashes = {}
        for song in __initsongs:
            songhash = song["hash"].lower()
            
            try:
                hashes[songhash] = {
                    "hash": songhash,
                    "songName": songsdict[songhash].name
                }
            except:
                hashes[songhash] = {
                    "hash": songhash,
                    "songName": "NOT DOWNLOADED"
                }

        self.songs = hashes
        
    def getData(self):
        namelist = []
        for songhash in self.songs:
            namelist.append(self.songs[songhash]["songName"])
        return namelist
    
    def getNames(self):
        return self.getData()

    def remove(self, songhash):
        self.songs.pop(songhash)

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