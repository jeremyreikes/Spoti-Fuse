from tqdm import tqdm
from parse_playlist import add_playlist
from database_querying import *
import csv
path = '/Users/jeremy/Desktop/Spoti-Fuse/pid_raw_data' # use your path
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
        if playlist_exists(pid):
            print(f'{pid} already parsed')
        else:
            add_playlist(pid)

# Uncomment to build database from spotify api
# build_database(all_files)
