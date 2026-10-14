"""Recommendation models: popularity baseline, BPR and home-country bonus."""

import numpy as np
import pandas as pd
from implicit.bpr import BayesianPersonalizedRanking
from scipy.sparse import csr_matrix

from src.metrics import K
from src.split import SEED


def popular_beers(train, home_country=None, home_bonus=0):
    """Beer ids sorted by popularity in train, most popular first.

    score = n_ratings / most ratings of any beer + home_bonus * (beer is from home_country)
    """
    counts = train.groupby("beer_id").agg(
        n_ratings=("beer_id", "size"), beer_country=("beer_country", "first")
    ).reset_index()
    counts["score"] = (
        counts["n_ratings"] / counts["n_ratings"].max()
        + home_bonus * (counts["beer_country"] == home_country)
    )
    # beer_id breaks ties so the order is the same every run
    counts = counts.sort_values(["score", "beer_id"], ascending=[False, True])
    return counts["beer_id"].tolist()


def recommend_popular(ranking, history, k=K):
    """Top k beers from the ranking for each user, skipping beers they already rated."""
    known = history.groupby("user_id")["beer_id"].apply(set)
    # At most len(known_beers) are skipped, so the first k + len(known_beers) are enough
    return {
        user_id: [beer for beer in ranking[: k + len(known_beers)] if beer not in known_beers][:k]
        for user_id, known_beers in known.items()
    }


def train_bpr(train, history, factors=64):
    """Fit BPR on train plus the Norwegian history and keep what is needed to recommend."""
    # The Norwegian history is included so the model knows a little about each test user
    ratings = pd.concat([train, history])
    user_codes, user_ids = pd.factorize(ratings["user_id"])
    beer_codes, beer_ids = pd.factorize(ratings["beer_id"])
    matrix = csr_matrix((np.ones(len(ratings), dtype=np.float32), (user_codes, beer_codes)))

    model = BayesianPersonalizedRanking(factors=factors, random_state=SEED)
    model.fit(matrix, show_progress=False)

    beer_countries = ratings.drop_duplicates("beer_id").set_index("beer_id")["beer_country"]
    return {
        "model": model,
        "matrix": matrix,
        "user_ids": user_ids,
        "beer_ids": beer_ids,
        "beer_countries": beer_countries.reindex(beer_ids).to_numpy(),
    }


def recommend_bpr(bpr, history, home_bonus=0, k=K):
    """Top k beers per user from BPR, skipping beers they already rated.

    score = BPR score + home_bonus * (beer is from the user's country)
    """
    users = history.drop_duplicates("user_id")
    rows = bpr["user_ids"].get_indexer(users["user_id"])
    is_home = {country: bpr["beer_countries"] == country for country in users["user_country"].unique()}

    recommendations = {}
    for user_id, country, row in zip(users["user_id"], users["user_country"], rows):
        scores = bpr["model"].item_factors @ bpr["model"].user_factors[row]
        scores = scores + home_bonus * is_home[country]
        scores[bpr["matrix"][row].indices] = -np.inf
        top_beers = np.argsort(-scores)[:k]
        recommendations[user_id] = list(bpr["beer_ids"][top_beers])
    return recommendations
