import pandas as pd
import numpy as np
import requests

# Define the URL for movie data
myurl = "https://liangfgithub.github.io/MovieData/movies.dat?raw=true"

# Fetch the data from the URL
response = requests.get(myurl)

# Split the data into lines and then split each line using "::"
movie_lines = response.text.split('\n')
movie_data = [line.split("::") for line in movie_lines if line]

# Create a DataFrame from the movie data
movies = pd.DataFrame(movie_data, columns=['movie_id', 'title', 'genres'])
movies['movie_id'] = movies['movie_id'].astype(int)

data_dir = "https://github.com/ranyou/psl/tree/main/MovieRS/data"

# Load similarity values
S = pd.read_csv(f"{data_dir}/Smat.csv", index_col=0)
# Load popularity values
P = pd.read_csv(f"{data_dir}/popularity.csv")

def get_displayed_movies():
    return movies.head(100)

def myIBCF(w): 
    pred = S.fillna(0) @ w.fillna(0) / (S.fillna(0) @ (1 - np.isnan(w)))
    recommended_movies = [
        int(m.lstrip('m')) for m in pred[np.isnan(w)].sort_values(ascending=False).head(10).dropna().index
    ]
    if len(recommended_movies) < 10: 
        unwatched_movies = np.array([int(m.lstrip('m')) for m in S.columns])[np.isnan(w)]
        additional_movies = P[P["MovieID"].isin(unwatched_movies)] \
            .sort_values("popularity", ascending=False)[:10-len(recommended_movies)]["MovieID"].values
        return list(recommended_movies) + list(additional_movies)
    return recommended_movies

def get_recommended_movies(new_user_ratings):
    w = pd.Series([np.nan for _ in range(len(S.columns))], index=S.columns)
    for movie_id, rating in new_user_ratings.items(): 
        w.loc[f"m{movie_id}"] = rating
    recommended_movies = myIBCF(w)
    return movies[movies.movie_id.isin(recommended_movies)]

