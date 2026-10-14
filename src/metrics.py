"""Recall@k, NDCG@k and Coverage@k with binary relevance."""

import numpy as np
import pandas as pd

K = 10


def recall_at_k(recommended, hidden, k=K):
    """Share of the user's hidden beers found in the top k."""
    hits = len(set(recommended[:k]) & hidden)
    return hits / len(hidden)


def ndcg_at_k(recommended, hidden, k=K):
    """Like recall, but hits near the top of the list count more."""
    dcg = sum(1 / np.log2(rank + 2) for rank, beer in enumerate(recommended[:k]) if beer in hidden)
    # Best possible score: every slot filled with a hit, as far as the user has hidden beers
    ideal = sum(1 / np.log2(rank + 2) for rank in range(min(k, len(hidden))))
    return dcg / ideal


def coverage_at_k(recommendations, n_beers, k=K):
    """Share of all beers that appear in at least one top-k list."""
    shown = {beer for recommended in recommendations.values() for beer in recommended[:k]}
    return len(shown) / n_beers


def user_scores(recommendations, hidden, k=K):
    """Recall and NDCG per user, as a table (useful for the failure analysis).

    recommendations: dict user_id -> list of beer_ids, best first.
    hidden: DataFrame with user_id and beer_id (the answer key).
    """
    hidden_sets = hidden.groupby("user_id")["beer_id"].apply(set)
    rows = [
        {
            "user_id": user_id,
            "recall": recall_at_k(recommendations[user_id], hidden_beers, k),
            "ndcg": ndcg_at_k(recommendations[user_id], hidden_beers, k),
        }
        for user_id, hidden_beers in hidden_sets.items()
    ]
    return pd.DataFrame(rows)


def evaluate(recommendations, hidden, n_beers, k=K):
    """Mean Recall@k and NDCG@k over users, plus Coverage@k."""
    scores = user_scores(recommendations, hidden, k)
    return {
        f"recall@{k}": scores["recall"].mean(),
        f"ndcg@{k}": scores["ndcg"].mean(),
        f"coverage@{k}": coverage_at_k(recommendations, n_beers, k),
    }
