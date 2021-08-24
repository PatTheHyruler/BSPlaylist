import pybeatsaver

beatsaber = pybeatsaver.BeatSaver()


class BeatSaver:
    @staticmethod
    async def get_hash_by_key(key):
        beatmap = await beatsaber.get_map_by_key(key)
        # TODO: idk how versions work so currently this just returns the first version from the list
        maphash = beatmap.versions[0].hash
        return maphash
