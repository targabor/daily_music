
def clean_track_data(track: dict):
    """
        Returns:
            track in list, duplicated if multiple artists present

        Args:
            track: response data from spotify api call on spotify_id
    """
    res = []
    track_artist = {"spotify_id": track['id'],
                    "artist_id": "N/A",
                    "title": track['name'],
                    "popularity": track['popularity']}
    
    for artist in track["artists"]:
        track_artist["artist_id"] = artist["id"]
        track_artist["artist_name"] = artist["name"]
        if "genres" in artist:
            track_artist["genres"] = [genre for genre in arist["genres"]]
        res.append(track_artist)
    else:
        res.append(track_artist)

    return res