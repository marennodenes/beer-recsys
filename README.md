# beer-recsys

A school project in Business Intelligence. We build a system that recommends beers, using ratings from the
website RateBeer.

**The idea:** A beer app is launching in Norway. It has many users in other countries, but none in Norway yet.
Can it still give good recommendations to its first Norwegian users?

This matters for business because a company entering a new market has little local data. If data from
other markets works, it can give good recommendations from day one.

## Questions and hypotheses

- **RQ1:** Can data from other countries give good recommendations to new users in Norway?
  - **H1:** A model trained on other countries beats simply recommending the most popular beers.
- **RQ2:** Does it help to look at where the beer comes from and which countries are similar to Norway?
  - **H2:** It helps to give a bonus to beers from the user's own country.
  - **H3:** Data from Nordic users (Sweden, Denmark, Finland) helps more than the same amount of data from
    other countries.

## How to run

Run this once from the project folder. It installs the libraries and downloads the data (about 1 GB):

```
python3 -m venv .venv          # Mac (Windows: python -m venv .venv)
source .venv/bin/activate      # Mac
.venv\Scripts\activate         # Windows
python setup_project.py
```

In VS Code, pick `.venv` as the Python interpreter. Then run the notebooks in order:

| Notebook | What it does | Time |
|---|---|---|
| `01_data_overview` | Loads and cleans the data | ~1 min |
| `02_split` | Splits the data into training data and test users | ~1 min |
| `03_models` | Trains and scores all models | 10+ min |
| `04_results` | Tables, figures, hypothesis tests and failure analysis | seconds |

## Data

RateBeer data from Lederrey & West (2018). It is not in the repo. `setup_project.py` downloads it.

We keep ratings from 2010 to mid-2017 and find each user's and brewery's country from their location.
After cleaning there are about 4.9 million ratings from 36,700 users. 609 of the users are Norwegian.

## How we test

1. **Training data:** all ratings from users outside Norway.
2. **Test users:** the 180 Norwegian users with at least 15 ratings.
3. The models only get each test user's **first 5 ratings**. The rest are hidden and used as the
   **answer key**.
4. The test users are split in two groups of 90: **validation** (to pick settings) and **test** (for the
   final numbers).

The hidden ratings are never used for training.

## Models

There are two models: **popularity** (the most rated beers) and **BPR** (learns which beers are liked by the
same people). The runs differ in training data or in a bonus.

| Run | What it is | Tests |
|---|---|---|
| Baseline | Most popular beers | (comparison point) |
| B | BPR on all other countries | H1 |
| C | B + bonus for beers from the user's country | H2 |
| D | BPR on Nordic users only | H3 |
| E | BPR on other countries, same amount of data as D | H3 |

## Measuring

Each model gives every test user a top 10. We compare it with the user's hidden beers:
- **Recall@10:** how many of the hidden beers are in the top 10.
- **NDCG@10:** like recall, but hits at the top count more. Our main measure.
- **Coverage@10:** how many different beers are recommended in total (variety).

## Results

See [04_results.ipynb](notebooks/04_results.ipynb) for all results and a summary. Tables and figures for the
report are in [results/](results/):

- [Main results](results/test_results.csv)
- [Hypothesis tests](results/hypothesis_tests.csv)
- [Figure: all runs](results/metrics_by_run.png)
- [Figure: failure analysis](results/failure_analysis.png)
- [Figure: D vs. E](results/failure_analysis_d_vs_e.png)

## Folders

```
data/        the data (not in git)
notebooks/   the four notebooks
src/         code the notebooks use
results/     tables and figures for the report
```

## Limitations

- Country is a rough way to measure culture.
- We know where the user lives, not where they drank the beer.
- People may drink local beer because it is what the shops sell, not because of taste.
- The data is from 2010–2017, and most users are from the US.
- Only 90 test users, so results can change a bit between groups.
- The best bonus and model size were the largest we tried. Larger values might work even better.
- The Nordic data (D) has fewer users with more ratings each than E. This may explain part of the difference.

## Reference

Lederrey, G., & West, R. (2018). When Sheep Shop: Measuring Herding Effects in Product Ratings with Natural
Experiments. *Proceedings of The Web Conference (WWW 2018)*.
