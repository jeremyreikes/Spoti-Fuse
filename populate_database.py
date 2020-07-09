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

# every once in a while an artist will not return anything from API, but will do so the next day
# Not sure what the bug is but run this every once in a while to reparse them
def reparse_unparsed_entities():
    refetch_unparsed_artists()


# Uncomment to build database from spotify api, uncomment reparse_unparsed_entities to ensure database integrity
# build_database(all_files)

# reparse_unparsed_entities()
