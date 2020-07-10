import lyricsgenius
import re
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
