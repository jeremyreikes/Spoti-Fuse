import warnings
warnings.filterwarnings('ignore')
from pymongo import MongoClient
client = MongoClient(readPreference='secondary')
spotify_db = client.spotify_db
tracks_db = spotify_db.tracks_db
playlists_db = spotify_db.playlists_db
artists_db = spotify_db.artists_db
from collections import Counter

def track_exists(tid):
    return tracks_db.count_documents({'_id': tid}, limit=1) == 1

def get_track(tid):
    return tracks_db.find_one({'_id': tid})

def playlist_exists(pid):
    return playlists_db.count_documents({'_id': pid}, limit=1) == 1

def get_playlist(pid):
    return playlists_db.find_one({'_id': pid})

def get_all_playlists():
    return playlists_db.find()

def artist_exists(aid):
    return artists_db.count_documents({'_id': aid}, limit=1) == 1

def get_artist(aid):
    return artists_db.find_one({'_id': aid})


# Use search_word to specify songs from playlists with a particular word in the title
def get_track_frequencies(search_word=None):
    frequencies = Counter()
    if search_word:
        playlists = playlists_db.find({'name_lemmas': search_word})
    else:
        playlists = playlists_db.find()
    # get frequency of song in playlist with 'word' in name
    for playlist in playlists:
        tids = playlist['tids']
        for tid in tids:
            frequencies[tid] += 1
    return frequencies

# given a tid, returns title and artist
def get_track_info(tid):
    track = tracks_db.find_one({'_id': tid})
    title = track['name']
    artist = artists_db.find_one({'_id': track['artist_id']})
    return (title, artist['name'])
