
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
                    "popularity": track['popularity'],
                    "genres": ','.join(track['album'].get('genres', [])),
                    "duration": track['duration_ms']}

    for artist in track["artists"]:
        track_artist["artist_id"] = artist["id"]
        res.append(track_artist.copy())
    if len(res) == 0:
        res.append(track_artist)

    return res


def get_new_artists(artists: list, new_artists: set):
    return [a for a in new_artists if a not in artists]


def get_new_genres(genre: list, new_genres: set):
    return [g for g in new_genres if g not in genre]


def make_genre_to_artist_pairs(artist_id: str, genres: list, genres_dict):
    """ Creates pairs for matching table for artists and its genres

        Returns:
            List of tuples with artist and genre:
                e.g.: [(atrist_id1, genre_id1), (atrist_id1, genre_id2)]

        Args:
            atrist_id: spotify artis_id
            genres: list of genres artist is associated with
    """
    res = []
    for genre in genres:
        res.append((artist_id, genres_dict[genre]))
    return res


def tuple_pairs_to_dict(genres: list):
    """ Converts a list of genre tuples to a dictionary

        Returns:
            Dictionary with the tuples first item as key and second as its value
        Args:
            genres: list of tuples containing two elements
    """
    return {name: id for (id, name) in genres}
