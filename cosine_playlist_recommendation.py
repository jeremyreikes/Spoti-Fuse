from pymongo import MongoClient
from sklearn.feature_extraction.text import CountVectorizer
import database_querying as dbq
from sklearn.metrics.pairwise import linear_kernel
from populate_database import add_playlist

def create_playlist_docs():
    playlist_docs = list()
    pids = list()
    playlists = dbq.get_all_playlists()
    for playlist in playlists:
        tracks = playlist['tids']
        doc = ' '.join(tracks)
        playlist_docs.append(doc)
        pids.append(playlist['_id'])
    return playlist_docs, pids

def create_playlist_doc(pid, cv):
    playlist = dbq.get_playlist(pid)
    tracks = playlist['tids']
    playlist_doc = ' '.join(tracks)
    return cv.transform([playlist_doc])

def init_playlist_matrix():
    playlist_docs, pids = create_playlist_docs()
    cv = CountVectorizer(binary=True, lowercase=False)
    csr_mat = cv.fit_transform(playlist_docs)
    return csr_mat, cv, pids

# Gets n most similar playlists to pid
def get_similar_playlists(pid, n=5):
    try:
        add_playlist(pid)
    except:
        print(f'Invalid Playlist_ID - {pid} - Try Again')
        return None
    user_playlist_doc = create_playlist_doc(pid, cv)
    cosine_similarities = linear_kernel(user_playlist_doc, csr_mat).flatten()
    related_playlist_indices = cosine_similarities.argsort()[-2:-2-n:-1] # this slice gets the top 5 most similar playlists (most similar is same playlist)
    recommended_playlists = list()
    for index in related_playlist_indices:
        curr_playlist = list()
        pid = pids[index]
        playlist = dbq.get_playlist(pid)
        tids = playlist['tids']
        for tid in tids:
            curr_playlist.append(dbq.get_track_info(tid))
        recommended_playlists.append(curr_playlist)
    return recommended_playlists

csr_mat, cv, pids = init_playlist_matrix()
pid = '6TX1GqG8qtlx8DuY4qrGnd'
recs = get_similar_playlists(pid, n=1)
