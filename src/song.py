import json
import os
from src.utils import sha1

class Song():
    def __init__(self, songpath):
        with open(os.path.join(songpath, "info.dat"), "r", encoding="utf8") as f:
            info = json.load(f)
        self.name = info["_songName"]
        self.subname = info["_songSubName"]
        self.author = info["_levelAuthorName"]
        self.bpm = info["_beatsPerMinute"]
        songfilename = info["_songFilename"]
        coverimagefilename = info["_coverImageFilename"]
        self.diff_files = []
        for difftype in info["_difficultyBeatmapSets"]:
            for diff in difftype["_difficultyBeatmaps"]:
                self.diff_files.append(os.path.join(songpath, diff["_beatmapFilename"]))
        files_to_hash = [item for item in self.diff_files]
        files_to_hash.insert(0, os.path.join(songpath, "Info.dat"))
        try:
            self.contributors = info["_customData"]["_contributors"]
        except:
            pass
        try:
            with open(os.path.join(songpath, "metadata.dat"), "r", encoding="utf8") as f:
                metadata = json.load(f)
            self.hash = metadata["hash"].lower()
        except:
            self.hash = sha1(files_to_hash).lower()
            print(files_to_hash)
            print(self.hash)
    pass