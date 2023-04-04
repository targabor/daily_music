
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
            track_artist["genres"] = [genre for genre in artist["genres"]]
        res.append(track_artist)
    else:
        res.append(track_artist)

    return res


def make_genre_to_artist_pairs(artist_genres: list):
    """ Creates pairs for matching table for artists and its genres

        Returns:
            List of two element list:
                e.g.: [[atrist_id1, genre_id1], [[atrist_id1, genre_id2]]

        Args:
            atrist_genres: list containing dict in format [{artist_id: artist_id, genres: [genre1, genre2...]}, ...]
    """
    res = []
    for artist in artist_genres:
        for genre in artist["genres"]:
            res.append[artist["artist_id"]]
            res.append(genre)
    return res
                