from gensim.models import Word2Vec
import database_querying as dbq
from populate_database import add_playlist

def create_model():
    playlists = dbq.get_all_playlists()
    playlists_tokenized = [playlist['tids'] for playlist in playlists]
    return Word2Vec(playlists_tokenized, min_count=5)

def get_similar_tracks(tids, n=5):
    # if only entering a track, convert to a list
    if type(tids) == str:
        tids = [tids]
    valid_tids = []
    vocab = model.wv.vocab.keys()
    for tid in tids:
        if tid in vocab:
            valid_tids.append(tid)
    track_similarities = model.most_similar(valid_tids)[:n]
    similar_tracks = [dbq.get_track_info(track[0]) for track in track_similarities]
    return similar_tracks

def playlist_addition_recommendations(pid, n=5):
    if not dbq.playlist_exists(pid):
        add_playlist(pid)
    tids = dbq.get_playlist_tids(pid)
    track_recs = get_similar_tracks(tids)
    return track_recs

# model = create_model()
# similar_tracks = get_similar_tracks('3ktdyyMjTjJikry5qPWIcj')
# playlist_addition_recs = playlist_addition_recommendations('0OqQxK6Keq5gfVmYNFtbbV')
