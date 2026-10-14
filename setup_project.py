"""One-time setup: install the libraries and download the data.

Run from the project folder:
    python setup_project.py
"""

import subprocess
import sys

print("Installing libraries from requirements.txt...")
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

# Imported after installing, since src.data needs pandas
from src.data import download_data, load_ratings

print("Downloading data...")
download_data()

print("Preparing ratings (takes a few minutes)...")
load_ratings()

print("Setup done")
