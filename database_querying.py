import warnings
warnings.filterwarnings('ignore')
from pymongo import MongoClient
client = MongoClient()
spotify_db = client.spotify_db
tracks_db = spotify_db.tracks_db
playlists_db = spotify_db.playlists_db
artists_db = spotify_db.artists_db
from collections import Counter
from nlp_helpers import lemmatize


def track_exists(tid):
    return tracks_db.count_documents({'_id': tid}, limit=1) == 1

def get_track(tid):
    return tracks_db.find_one({'_id': tid})

def playlist_exists(pid):
    return playlists_db.count_documents({'_id': pid}, limit=1) == 1

def get_playlist(pid):
    return playlists_db.find_one({'_id': pid})

def get_playlist_tids(pid):
    playlist = get_playlist(pid)
    return playlist['tids']

def get_all_playlists():
    return playlists_db.find()

def artist_exists(aid):
    return artists_db.count_documents({'_id': aid}, limit=1) == 1

def get_artist(aid):
    return artists_db.find_one({'_id': aid})

def insert_tracks(tracks):
    if tracks:
        try:
            tracks_db.insert_many(tracks)
        except:
            for track in tracks:
                try:
                    tracks_db.insert_one(track)
                except:
                    print(f'Cannot insert track: {track}')

def insert_artists(artists):
    if artists:
        try:
            artists_db.insert_many(artists)
        except BulkWriteError as bwe:
            for artist in artists:
                try:
                    artists_db.insert_one(artist)
                except:
                    print(f'Cannot insert artist {artist}')

def replace_artist(artist_data):
    artists_db.find_one_and_replace({'_id': artist_data['_id']}, artist_data)

def insert_playlist(playlist):
    playlists_db.insert_one(playlist)

def add_pid_to_track(tid, pid):
    tracks_db.update_one({'_id': tid}, {'$push': {'pids': pid}})

def add_lyrics_to_track(tid, lyrics):
    tracks_db.update_one({'_id': tid}, {'$set': {'lyrics': lyrics}})

def get_tracks_without_lyrics():
    return tracks_db.find({'lyrics': {'$exists': False}}, {'_id': 1})

# Spotify API sometimes fails and returns a 404 on an artist, but then it will work the next day
# Run get_unparsed_artists_count() every once in a while to verify that all artists are parsed
def get_unparsed_artists():
    return artists_db.find({'name': {'$exists': False}}, {})
def get_unparsed_artist_count():
    unparsed_artists = get_unparsed_artists()
    return unparsed_artists.count()

# Use search_word to specify songs from playlists with a particular word in the title
def get_track_frequencies(search_words):
    # dict - word, counter
    word_track_frequencies = dict()
    lemmas = lemmatize(search_words)
    for lemma in lemmas:
        frequencies = Counter()
        playlists = playlists_db.find({'name_lemmas': lemma})
        for playlist in playlists:
            tids = playlist['tids']
            for tid in tids:
                frequencies[tid] += 1
        word_track_frequencies[lemma] = frequencies
    return word_track_frequencies

# given a tid, returns title and artist
def get_track_info(tid):
    track = tracks_db.find_one({'_id': tid})
    title = track['name']
    artist = artists_db.find_one({'_id': track['artist_id']})
    return (title, artist['name'])

# playlists_db.find(limit=5)[3]
