"""Split the data into training data and Norwegian test/validation users."""

import numpy as np
import pandas as pd

from src.data import PROCESSED_DIR

SEED = 42
TARGET_COUNTRY = "Norway"
MIN_RATINGS = 15
N_HISTORY = 5
SPLIT_FILES = ("train", "history", "hidden")


def split_history_hidden(target_ratings):
    """First N_HISTORY ratings per user as history, the rest as hidden."""
    # Dates are per day, so beer_id breaks ties to keep the order fixed
    target_ratings = target_ratings.sort_values(["user_id", "date", "beer_id"])
    position = target_ratings.groupby("user_id").cumcount()
    return target_ratings[position < N_HISTORY], target_ratings[position >= N_HISTORY]


def assign_groups(user_ids):
    """Randomly label half the users 'validation' and half 'test'."""
    shuffled = np.random.default_rng(SEED).permutation(np.sort(user_ids))
    half = len(shuffled) // 2
    groups = ["validation"] * half + ["test"] * (len(shuffled) - half)
    return pd.Series(groups, index=shuffled, name="group")


def make_split(ratings):
    """Return train, history and hidden from the clean ratings.

    train: all ratings from users outside the target country.
    history/hidden: target users with at least MIN_RATINGS ratings, with a 'group' column.
    Other target-country ratings are not used at all.
    """
    train = ratings[ratings["user_country"] != TARGET_COUNTRY]
    target = ratings[ratings["user_country"] == TARGET_COUNTRY]
    counts = target["user_id"].value_counts()
    target = target[target["user_id"].isin(counts[counts >= MIN_RATINGS].index)]

    history, hidden = split_history_hidden(target)
    groups = assign_groups(target["user_id"].unique())
    history = history.assign(group=history["user_id"].map(groups))
    hidden = hidden.assign(group=hidden["user_id"].map(groups))
    return train.reset_index(drop=True), history.reset_index(drop=True), hidden.reset_index(drop=True)


def save_split(train, history, hidden):
    """Save the split to data/processed/ as parquet."""
    for name, table in zip(SPLIT_FILES, (train, history, hidden)):
        table.to_parquet(PROCESSED_DIR / f"{name}.parquet", index=False)


def load_split():
    """Load train, history and hidden from data/processed/."""
    return tuple(pd.read_parquet(PROCESSED_DIR / f"{name}.parquet") for name in SPLIT_FILES)
