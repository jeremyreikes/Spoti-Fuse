from sklearn.feature_extraction.text import CountVectorizer
import database_querying as dbq
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from populate_database import add_playlist
# from surprise import SVD, evaluate

def prep_playlists():
    playlist_docs = list()
    pid_index = list()
    playlists = dbq.get_all_playlists()
    for playlist in playlists:
        tracks = playlist['tids']
        doc = ' '.join(tracks)
        playlist_docs.append(doc)
        pid_index.append(playlist['_id'])
    return playlist_docs, pid_index

def create_playlist_doc(pid, cv):
    playlist = dbq.get_playlist(pid)
    tracks = playlist['tids']
    playlist_doc = ' '.join(tracks)
    return cv.transform([playlist_doc])

def get_matching_row(matrix, pid=None, tid=None):
    if tid:
        index = tid_index.index(tid)
    elif pid:
        index = pid_index.index(pid)
    return matrix[index]

def init_matrix():
    playlist_docs, pid_index = prep_playlists()
    cv = CountVectorizer(binary=True, lowercase=False)
    csr_mat = cv.fit_transform(playlist_docs)
    tid_index = cv.get_feature_names()
    return csr_mat, cv, pid_index, tid_index

# Gets n most similar playlists to pid
def get_playlist_recs(related_indices, pid_index):
    recommended_playlists = list()
    for index in related_indices:
        curr_playlist = list()
        pid = pid_index[index]
        playlist = dbq.get_playlist(pid)
        tids = playlist['tids']
        for tid in tids:
            curr_playlist.append(dbq.get_track_info(tid))
        recommended_playlists.append(curr_playlist)
    return recommended_playlists

def get_track_recs(related_indices, tid_index):
    recommended_tracks = list()
    for index in related_indices:
        tid = tid_index[index]
        track = dbq.get_track_info(tid)
        recommended_tracks.append(track)
    return recommended_tracks

def trim_indices(id, related_indices, index):
    if index[related_indices[0]] == id:
        return related_indices[1:]
    else:
        return related_indices[:-1]


csr_mat, cv, pid_index, tid_index = init_matrix() #

def get_recommendations(tid=None, pid=None, n=5):
    if pid:
        matrix = csr_mat
        try:
            add_playlist(pid)
            row_to_compare = create_playlist_doc(pid, cv)
        except:
            # print(f'Invalid Playlist_ID - {pid} - Try Again')
            return None
    elif tid:
        # Transpose original matrix to get track recommendations
        matrix = csr_mat.T
        try:
            row_to_compare = get_matching_row(matrix, tid=tid)
        except:
            print(f'Invalid Track_ID - {tid} - Try Again')
            return None
    else:
        print(f'Please enter a Playlist or Track ID')
        return None
    similarities = cosine_similarity(row_to_compare, matrix).flatten()
    related_indices = similarities.argsort()[-1:-2-n:-1] # this slice gets the top 5 most similar playlists (most similar is same playlist
    if pid:
        related_indices = trim_indices(pid, related_indices, pid_index)
        return get_playlist_recs(related_indices, pid_index)
    if tid:
        related_indices = trim_indices(tid, related_indices, tid_index)
        return get_track_recs(related_indices, tid_index)

# predicts what songs should be added to playlists
def svd_recs(data, playlist, pid, cv):
    svd = SVD()
    evaluate(svd, data, measures=['RMSE', 'MAE'])
    trainset = data.build_full_trainset()
    svd.train(trainset)
    playlist_doc = create_playlist_doc(pid, cv)
    preds = svd.predict(playlist_doc).est
dbq.get_playlist('1Brkw1Qa7byjfanaNdyH6m')
pid = '0FfrY7bwlxZLBZChI2RNwB'
recs = get_recommendations(pid=pid)


import pyspark
import keras
pyspark.__version__
