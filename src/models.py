"""Recommendation models: popularity baseline and BPR (home-country bonus comes later)."""

import numpy as np
import pandas as pd
from implicit.bpr import BayesianPersonalizedRanking
from scipy.sparse import csr_matrix

from src.metrics import K
from src.split import SEED


def popular_beers(train):
    """Beer ids sorted by number of ratings in train, most rated first."""
    counts = train.groupby("beer_id").size().reset_index(name="n_ratings")
    # beer_id breaks ties so the order is the same every run
    counts = counts.sort_values(["n_ratings", "beer_id"], ascending=[False, True])
    return counts["beer_id"].tolist()


def recommend_popular(ranking, history, k=K):
    """Top k beers from the ranking for each user, skipping beers they already rated."""
    known = history.groupby("user_id")["beer_id"].apply(set)
    # At most len(known_beers) are skipped, so the first k + len(known_beers) are enough
    return {
        user_id: [beer for beer in ranking[: k + len(known_beers)] if beer not in known_beers][:k]
        for user_id, known_beers in known.items()
    }



def recommend_bpr(train, history, factors=64, k=K):
    """Top k beers from a BPR model for each user in history, skipping beers they already rated."""
    # The Norwegian history is included so the model knows a little about each test user
    ratings = pd.concat([train, history])
    user_codes, user_ids = pd.factorize(ratings["user_id"])
    beer_codes, beer_ids = pd.factorize(ratings["beer_id"])
    matrix = csr_matrix((np.ones(len(ratings), dtype=np.float32), (user_codes, beer_codes)))

    model = BayesianPersonalizedRanking(factors=factors, random_state=SEED)
    model.fit(matrix, show_progress=False)

    users = history["user_id"].unique()
    rows = user_ids.get_indexer(users)
    top_beers, _ = model.recommend(rows, matrix[rows], N=k, filter_already_liked_items=True)
    return {user_id: list(beer_ids[beers]) for user_id, beers in zip(users, top_beers)}
