from sklearn.feature_extraction.text import CountVectorizer
import database_querying as db
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from populate_database import add_playlist
import surprise
from scipy.sparse.linalg import svds
import numpy as np
import scipy


class SVD:
    def __init__(self, k=50):
        self.init_matrix()
        self.u, self.s, self.v = svds(self.csr_mat.astype('float'), k = k)

    def prep_playlists(self):
        playlist_docs = list()
        pid_index = list()
        playlists = db.get_all_playlists()
        for playlist in playlists:
            tracks = playlist['tids']
            doc = ' '.join(tracks)
            playlist_docs.append(doc)
            pid_index.append(playlist['_id'])
        self.playlist_docs = playlist_docs
        self.pid_index = pid_index
        return playlist_docs, pid_index

    def init_matrix(self):
        self.prep_playlists()
        self.cv = CountVectorizer(binary=True, lowercase=False)
        self.csr_mat = self.cv.fit_transform(self.playlist_docs)
        self.tid_index = self.cv.get_feature_names()

    def create_playlist_doc(self, pid, cv):
        playlist = db.get_playlist(pid)
        tracks = playlist['tids']
        playlist_doc = ' '.join(tracks)
        return cv.transform([playlist_doc])

    def get_matching_row(self, pid=None, tid=None):
        if tid:
            index = self.tid_index.index(tid)
        elif pid:
            index = self.pid_index.index(pid)
        return self.csr_mat[index]

    # Gets n most similar playlists to pid
    def get_playlist_recs(self, related_indices):
        recommended_playlists = list()
        for index in related_indices:
            curr_playlist = list()
            pid = self.pid_index[index]
            playlist = db.get_playlist(pid)
            tids = playlist['tids']
            for tid in tids:
                curr_playlist.append(db.get_track_info(tid))
            recommended_playlists.append(curr_playlist)
        return recommended_playlists

    def get_track_recs(self, related_indices):
        recommended_tracks = list()
        for index in related_indices:
            tid = self.tid_index[index]
            track = db.get_track_info(tid)
            recommended_tracks.append(track)
        return recommended_tracks

    def get_recommendations(self, tid=None, pid=None, n=5):
        if pid:
            valid_playlist = add_playlist(pid)
            if valid_playlist:
                if pid not in self.pid_index:
                    self.pid_index.append(pid)
                    row_to_add = self.create_playlist_doc(pid, self.cv)
                    self.csr_mat = scipy.sparse.vstack((self.csr_mat, row_to_add))
                    self.u, self.s, self.v = svds(self.csr_mat.astype('float'), k = k)
                    row_to_compare = -1
                else:
                    row_to_compare = self.pid_index.index(pid)
                self.similarities = cosine_similarity([self.u[row_to_compare]], self.u)
            else:
                return None
        elif tid:
            # Transpose original matrix to get track recommendations
            try:
                row_to_compare = self.tid_index.index(tid)
                self.similarities = cosine_similarity([self.v.T[row_to_compare]], self.v.T)
            except:
                print(f'Invalid Track_ID - {tid} - Try Again')
                return None
        else:
            print(f'Please enter a Playlist or Track ID')
            return None
        related_indices = self.similarities[0].argsort()[-2:-3-n:-1] # this slice gets the top 5 most similar playlists (most similar is same playlist)
        if pid:
            return self.get_playlist_recs(related_indices)
        if tid:
            return self.get_track_recs(related_indices)
