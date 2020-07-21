from tqdm import tqdm
from parse_playlist import fetch_playlist, refetch_unparsed_artists
import database_querying as db
import csv
path = '/Users/jeremyreikes/Desktop/Spoti-Fuse/pid_raw_data' # use your path
import glob
from twitter_scrape import get_tweets
import lyrics
all_files = glob.glob(path + "/*.csv")

def build_database(all_files):
    all_pids = set()
    for file in all_files:
        with open(file, 'r') as f:
          reader = csv.reader(f)
          lines = list(reader)
          for line in lines:
              all_pids.add(line[1])
    for pid in tqdm(list(all_pids)):
        add_playlist(pid)

def add_playlist(pid, update=False):
    # returns True if the playlist
    if db.playlist_exists(pid):
        if update: # if it exists, update it
            pass
        return True
    else:
        return fetch_playlist(pid) # returns true if playlist was successfully added

def add_lyrics(tid):
    track_lyrics = lyrics.fetch_lyrics(tid)
    if isinstance(track_lyrics, str):
        db.add_lyrics(tid, track_lyrics)

def add_lyrics_to_all_tracks():
    all_lyricless_tracks = db.get_tracks_without_lyrics()
    for track in all_lyricless_tracks:
        add_lyrics(track['_id'])

def add_tweets(tid):
    track = db.get_track(tid)
    if 'tweets' not in track:
        tweets = get_tweets(tid)
        db.add_tweets(tweets)

def add_tweets_to_all_tracks():
    # checks if 'tweets' is in track twice - will have higher runtime
    all_tweetless_tracks = db.get_tracks_without_tweets()
    for track in all_tweetless_tracks:
        add_tweets(track['_id'])


# Uncomment to build database from spotify api, uncomment reparse_unparsed_entities to ensure database integrity
# refetch_unparsed_artists()
# build_database(all_files)
