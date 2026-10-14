"""Download and load the RateBeer data."""

import gzip
import shutil
import tarfile
import urllib.request
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
RELEASE_URL = (
    "https://github.com/marennodenes/beer-recsys/releases/download/data-v1/beerDataset.tar.gz"
)
# reviews.txt.gz is skipped: same ratings with text, and almost 1 GB
NEEDED_FILES = {"ratings.txt.gz", "users.csv", "breweries.csv", "beers.csv"}

START_DATE = "2010-01-01"
END_DATE = "2017-07-31"
UK_PARTS = {"England", "Scotland", "Wales", "Northern Ireland"}


def download_data():
    """Download the needed files from the GitHub release into data/raw/, if missing."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    missing = {name for name in NEEDED_FILES if not (RAW_DIR / name).exists()}
    if not missing:
        return

    print(f"Downloading {', '.join(sorted(missing))} (takes a few minutes)...")
    # Stream the archive and extract only the needed files,
    # so the 1.9 GB tar.gz is never stored on disk
    with urllib.request.urlopen(RELEASE_URL) as response:
        with tarfile.open(fileobj=response, mode="r|gz") as archive:
            for member in archive:
                name = Path(member.name).name
                if name in missing:
                    with archive.extractfile(member) as src, open(RAW_DIR / name, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    print(f"  saved {name}")
    print("Done")


def load_users():
    """Load users.csv (downloads the data first if needed)."""
    download_data()
    return pd.read_csv(RAW_DIR / "users.csv")


def load_breweries():
    """Load breweries.csv (downloads the data first if needed)."""
    download_data()
    return pd.read_csv(RAW_DIR / "breweries.csv")


def load_beers():
    """Load beers.csv (downloads the data first if needed)."""
    download_data()
    return pd.read_csv(RAW_DIR / "beers.csv")


def load_ratings():
    """Load all ratings as user_id, beer_id, brewery_id, date, rating.

    The raw file is slow to read, so the result is saved to
    data/processed/ratings_raw.parquet the first time and read from there after.
    """
    cache = PROCESSED_DIR / "ratings_raw.parquet"
    if cache.exists():
        return pd.read_parquet(cache)

    download_data()
    print("Reading ratings.txt.gz (takes a few minutes the first time)...")
    rows, row = [], {}
    with gzip.open(RAW_DIR / "ratings.txt.gz", "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            key, _, value = line.partition(": ")
            if key in ("beer_id", "brewery_id", "date", "user_id"):
                row[key] = value.strip()
            elif key == "rating":
                row["rating"] = value.strip()
                rows.append(row)
                row = {}

    ratings = pd.DataFrame(rows)
    for col in ("user_id", "beer_id", "brewery_id"):
        ratings[col] = pd.to_numeric(ratings[col], errors="coerce").astype("Int64")
    ratings["rating"] = pd.to_numeric(ratings["rating"], errors="coerce")
    ratings["date"] = pd.to_datetime(pd.to_numeric(ratings["date"], errors="coerce"), unit="s")
    ratings = ratings[["user_id", "beer_id", "brewery_id", "date", "rating"]]

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ratings.to_parquet(cache, index=False)
    return ratings


def country_from_location(location):
    """Country from a location column: text before the first comma, UK parts merged."""
    country = location.str.split(",").str[0].str.strip()
    return country.replace(dict.fromkeys(UK_PARTS, "United Kingdom"))


def load_clean_ratings():
    """Ratings from 2010-01-01 to 2017-07-31 with user_country and beer_country.

    Users with no location and duplicate user-beer pairs are dropped.
    Saved to data/processed/ratings_clean.parquet the first time.
    """
    cache = PROCESSED_DIR / "ratings_clean.parquet"
    if cache.exists():
        return pd.read_parquet(cache)

    ratings = load_ratings()
    ratings = ratings[ratings["date"].between(START_DATE, f"{END_DATE} 23:59:59")]

    # users.csv lists a few users more than once
    users = load_users().dropna(subset=["location"]).drop_duplicates("user_id")
    users["user_country"] = country_from_location(users["location"])
    breweries = load_breweries().rename(columns={"id": "brewery_id"})
    breweries["beer_country"] = country_from_location(breweries["location"])

    ratings = ratings.merge(users[["user_id", "user_country"]], on="user_id")
    ratings = ratings.merge(breweries[["brewery_id", "beer_country"]], on="brewery_id", how="left")
    # Keep the first rating when a user rated the same beer twice
    ratings = ratings.sort_values("date").drop_duplicates(["user_id", "beer_id"])
    ratings = ratings.reset_index(drop=True)

    ratings.to_parquet(cache, index=False)
    return ratings
