import spacy
nlp = spacy.load('en_core_web_sm')
from pymongo import MongoClient
client = MongoClient(readPreference='secondary')
db = client.spotify_db
tracks_db = db.tracks_db
playlists_db = db.playlists_db
artists_db = db.artists_db


def lemmatize(text, return_lang=False):
    doc = nlp(text)
    lemmas = list()
    for token in doc:
        if token.is_stop or not token.is_alpha:
            continue
        lemma = token.lemma_.strip().lower()
        if lemma:
            lemmas.append(lemma)
    lemmas = list(set(lemmas))
    if return_lang:
        return lemmas, doc.lang_
    return lemmas
