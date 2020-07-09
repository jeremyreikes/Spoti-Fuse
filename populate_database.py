from tqdm import tqdm
from parse_playlist import fetch_playlist, refetch_unparsed_artists
from database_querying import playlist_exists
import csv
path = '/Users/jeremyreikes/Desktop/Spoti-Fuse/pid_raw_data' # use your path
import glob
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
    if playlist_exists(pid):
        # print(f'{pid} already parsed')
        if update: # if it exists, update it
            # try: update
            # except: print('cant update')
            pass
        return True
    else:
        return fetch_playlist(pid) # returns true if playlist was successfully added

# Uncomment to build database from spotify api, uncomment reparse_unparsed_entities to ensure database integrity
# refetch_unparsed_artists()
# build_database(all_files)
