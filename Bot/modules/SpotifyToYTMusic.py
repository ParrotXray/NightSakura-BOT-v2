from ytmusicapi import YTMusic

class ToYTMusicAddons():
    async def to_ytmusic(self, songs):
        query = f"{songs[0].get('artist')} - {songs[0].get('name')}".replace(
                        ":", ""
        ).replace('"', "")
        for count in range (len(YTMusic().search(query))):
            try:
                video_id = YTMusic().search(query)[count]['videoId']
                break
            except KeyError:
                continue

        return 'https://music.youtube.com/watch?v=' + video_id