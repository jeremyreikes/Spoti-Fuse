from pymongo import MongoClient
client = MongoClient()
spotify_db = client.spotify_db
playlists_db = spotify_db.playlists_db
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

def create_docs():
    docs = []
    for playlist in playlists_db.find():
        tracks = playlist['tids']
        doc = ' '.join(tracks)
        docs.append(doc)
    return docs

def playlist_matrix():
    docs = create_docs()
    cv = CountVectorizer(binary=True, lowercase=False)
    csr_mat = cv.fit_transform(docs)
    return csr_mat, cv
