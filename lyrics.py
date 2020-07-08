import pandas as pd
import lyricsgenius
import re
from tqdm import tqdm
from api_keys import genius_client_access_token
import database_querying as db
genius = lyricsgenius.Genius(genius_client_access_token)
genius.remove_section_headers = True
genius.verbose = False

def fetch_lyrics(tid):
    try:
        track = db.get_track(tid)
        tid = track['_id']
        track_name = track['name']
        if 'lyrics' in track:
            return None
        artist_name = db.get_artist(track['artist_id'])['name']
        song = genius.search_song(track_name, artist_name)
        if song:
            lyrics = song.lyrics
            if lyrics:
                lyrics = lyrics.replace('\n', '. ').replace('\u2005', ' ')
                regex = re.compile('([\][])')
                lyrics = re.sub(regex, '', lyrics)
                lyrics = lyrics.replace('. .', '.')
                return lyrics
        return str()
    except:
        return str()

def add_lyrics_to_track(tid):
    lyrics = fetch_lyrics(tid)
    if isinstance(lyrics, str):
        db.add_lyrics_to_track(tid, lyrics)

def add_lyrics_to_all_tracks():
    all_lyricless_tracks = db.get_tracks_without_lyrics()
    for track in all_lyricless_tracks:
        add_lyrics_to_track(track['_id'])
