import requests
import json

headers = {
    'authority': 'beatsaver.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'accept-language': 'en-US,en;q=0.9,et;q=0.8',
}


class BeatSaver:
    @staticmethod
    def get_hash_by_key(key):
        r = requests.get(f"https://beatsaver.com/api/maps/detail/{key}", headers=headers).text
        if r == "Not Found":
            return None
        songdata = json.loads(r)
        return songdata["hash"]
