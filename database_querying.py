import warnings
warnings.filterwarnings('ignore')
from pymongo import MongoClient
client = MongoClient(readPreference='secondary')
spotify_db = client.spotify_db

def track_exists(tid):
    return spotify_db.tracks_db.count_documents({'_id': tid}, limit=1) == 1

def playlist_exists(pid):
    return spotify_db.playlists_db.count_documents({'_id': pid}, limit=1) == 1

def artist_exists(aid):
    return spotify_db.artists_db.count_documents({'_id': aid}, limit=1) == 1
