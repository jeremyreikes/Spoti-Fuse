from gensim.models import Word2Vec
import database_querying as db
from populate_database import add_playlist

def create_model():
    playlists = db.get_all_playlists()
    playlists_tokenized = [playlist['tids'] for playlist in playlists]
    return Word2Vec(playlists_tokenized, min_count=10)

def get_similar_tracks(tids, n=10):
    # if only entering a track, convert to a list
    if type(tids) == str:
        tids = [tids]
    valid_tids = []
    vocab = model.wv.vocab.keys()
    for tid in tids:
        if tid in vocab:
            valid_tids.append(tid)
    track_similarities = model.most_similar(valid_tids)[:n]
    similar_tracks = [db.get_track_info(track[0]) for track in track_similarities]
    return similar_tracks

def playlist_addition_recommendations(pid, n=10):
    if not db.playlist_exists(pid):
        add_playlist(pid)
    tids = db.get_playlist_tids(pid)
    track_recs = get_similar_tracks(tids)
    return track_recs
