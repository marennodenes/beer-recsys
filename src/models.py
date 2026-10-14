"""Recommendation models: popularity baseline (BPR and home-country bonus come later)."""

from src.metrics import K


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
