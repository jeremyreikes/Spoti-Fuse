from sklearn.feature_extraction.text import CountVectorizer
import database_querying as db
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from populate_database import add_playlist
import surprise

def prep_playlists():
    playlist_docs = list()
    pid_index = list()
    playlists = db.get_all_playlists()
    for playlist in playlists:
        tracks = playlist['tids']
        doc = ' '.join(tracks)
        playlist_docs.append(doc)
        pid_index.append(playlist['_id'])
    return playlist_docs, pid_index

def create_playlist_doc(pid, cv):
    playlist = db.get_playlist(pid)
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
        playlist = db.get_playlist(pid)
        tids = playlist['tids']
        for tid in tids:
            curr_playlist.append(db.get_track_info(tid))
        recommended_playlists.append(curr_playlist)
    return recommended_playlists

def get_track_recs(related_indices, tid_index):
    recommended_tracks = list()
    for index in related_indices:
        tid = tid_index[index]
        track = db.get_track_info(tid)
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
        valid_playlist = add_playlist(pid)
        if valid_playlist:
            row_to_compare = create_playlist_doc(pid, cv)
        else:
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

'''
def svd_recs(data, playlist, pid, cv):
    svd = surprise.SVD()
    reader = surprise.Reader()
    help(data)
    help(svd)
    surprise.evaluate(svd, data, measures=['RMSE', 'MAE'])
    trainset = data.build_full_trainset()
    svd.train(trainset)
    playlist_doc = create_playlist_doc(pid, cv)
    preds = svd.predict(playlist_doc).est
'''

pid = '5d4FPOzRUnPgoq1TKigtKm'
tid = '24Yi9hE78yPEbZ4kxyoXAI'

recs = get_recommendations(tid=tid, n =5)
recs
