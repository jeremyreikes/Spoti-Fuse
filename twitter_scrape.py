import twint
import nest_asyncio
nest_asyncio.apply()
import pandas as pd
import time
import re

def get_playlist_id(row):
    regex = re.findall(r'\bplaylist\b\/\w*', row)
    if regex:
        return regex[0][9:]

# Scrapes playlists 1 day at a time...
def scrape_playlists(since=None, until=None):
    c = twint.Config()
    c.Pandas = True
    c.Pandas_clean = True
    c.Hide_output = True
    c.Until = until
    c.Since = since
    c.Limit = 15000
    c.Search = 'open.spotify.com/playlist/'
    try:
        twint.run.Search(c)
    except:
        print(f'Failed to complete search for {since}')
        scrape_playlists(since, until)
    df = twint.storage.panda.Tweets_df
    df['playlist_id'] = df['tweet'].apply(get_playlist_id)
    df.dropna(subset=['playlist_id'], inplace=True)
    df.drop_duplicates('playlist_id', inplace=True)
    df[['playlist_id', 'date']].to_csv(f'pid_raw_data/{since}.csv', mode='a+', header=False)
    until = since
    since_full = pd.to_datetime(df.iloc[-1]['date']) - pd.DateOffset(1) # subtract a day from since date
    since_arg = str(since_full)[:10]
    time.sleep(500)
    scrape_playlists(since_arg, until)

def get_tweets(tid):
    c = twint.Config()
    c.Pandas = True
    c.Pandas_clean = True
    c.Hide_output = True
    c.Lang = 'en'
    c.Limit=1000
    c.Search = f'open.spotify.com/track/{tid}'
    df = twint.storage.panda.Tweets_df
    tweets=  df.tweet
    geos = df.geo
    return zip(list(df.tweet), list(geos))


# scrape_playlists(since='2020-04-03', until='2020-04-04')
