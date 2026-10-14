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
    data/processed/ratings.parquet the first time and read from there after.
    """
    cache = PROCESSED_DIR / "ratings.parquet"
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
