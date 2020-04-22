from gensim.models import Word2Vec
import database_querying as dbq

def create_model():
    playlists = dbq.get_all_playlists()
    playlists_tokenized = [playlist['tids'] for playlist in playlists]
    return Word2Vec(playlists_tokenized)

def get_similar_tracks(tid, n=5):
    track_similarities = model.most_similar(tid)[:n]
    similar_tracks = [dbq.get_track_info(track[0]) for track in track_similarities]
    return similar_tracks

# model = create_model()
# coffee = '24Yi9hE78yPEbZ4kxyoXAI'
# tracks = get_similar_tracks(coffee)
# tracks
#
# dbq.get_track('2alc8VZAzDgdAsL2QMk3hu')
# dbq.get_artist('3O5HD95HTEPgoPFOjAb7yV')
