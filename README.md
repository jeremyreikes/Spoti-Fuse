# Spoti-Fuse
Spotifuse gives Spotify users the power to flexibly organize their libraries and discover new music.

### Technologies
Spotifuse leverages a variety of technologies to scrape, store, and analyze millions of playlists.
- Twint for Twitter scraping
- Spotipy for Spotify API
- MongoDB to store data
- Word2Vec, Scikit-Learn, and Surprise for song and playlist recommendations

## Getting the data
By using Twint, Spotifuse can bypass Twitter API limits and scrape an (essentially) unlimited number of playlists shared on Twitter.  It typically found ~10,000-15,000 unique playlists per day.  All of those playlists were queried using Spotipy and stored in MongoDB, including all relevant metadata (song metrics, artist information, etc).

## Recommendations
Spotifuse produces recommendations via several different implementations of collaborative-filtering, each being useful in its own right.  
- Weighted track frequency
    - Enter a playlist title and receive the top songs associated with playlists of similar titles.
- Cosine Similarity
    - Using playlist-song relationships, find the most similar songs or playlists.
- Singular Value Decomposition (SVD)
    - Scikit-Surprise is used for an SVD based recommender.  Find songs to add to an existing playlist.  (Module not loading on Mac OS machines as of 4/22/20.  Working on fix.).
- Song Embeddings
    - Playlists are thought of as documents and songs as words.  The embeddings are trained using Gensim's Word2Vec model, which can then be used for track recommendations.

## Evaluation
Given the sparsity and innate variance of playlists, it's hard to quantitatively evaluate the recommendations.  I'm working on implementing a genre prediction model as it might accurately represent a concept captured by SVD or Word2Vec.

## Update
Updated ReadME coming 4/29/2020.  Visualizations and analytics will be included.
