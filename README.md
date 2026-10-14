# beer-recsys

A school project for a Business Intelligence course. We build a system that recommends beers to users,
using real rating data from the website RateBeer. We test if ratings from people in other countries can
help give good recommendations to new users in Norway, and if it helps to look at where the beer comes
from and how culturally similar countries are.

## Research questions

> **RQ1:** Can data from users in other countries give good beer recommendations to new users in Norway?
>
> **RQ2:** Do recommendations improve when we consider where the beer comes from and how culturally
> similar the countries are?

RQ1 is answered by H1. RQ2 is answered by H2 (where the beer comes from) and H3 (cultural similarity).

## Scenario

An international beer app is launching in Norway. It already has many users in other countries, but no
Norwegian users yet. The first Norwegian users rate a few beers each. What should the app recommend to them?

Why this matters for business:
- Good recommendations help new customers find products they like, which keeps them using the app.
- A company entering a new market has little local data. If data from existing markets works, it can grow faster.
- It helps decide whether to promote local products and which markets' data is most useful.

## Hypotheses

- **H1 (transfer):** A model trained on users from other countries gives better recommendations to new
  Norwegian users than simply recommending the most popular beers.
- **H2 (home country):** Recommendations improve when the model knows whether a beer comes from the
  user's own country.
- **H3 (cultural similarity):** Data from Nordic users (Sweden, Denmark, Finland) helps Norwegian users more
  than the same amount of data from the rest of the world.

## Data

RateBeer data from Lederrey & West (2018), "When Sheep Shop" (WWW 2018). Not included in the repo.
Download `beerDataset.tar.gz` from the `data-v1` release and unpack it into `data/raw/`.

| File | Used for |
|---|---|
| `ratings.txt.gz` | One rating per record: user_id, beer_id, brewery_id, date, rating (1–5) |
| `users.csv` | `location` = user's country (US users as "United States, <State>") |
| `breweries.csv` | `location` = brewery's country |
| `beers.csv` | Beer name, style, ABV |

`reviews.txt.gz` is not needed (same ratings with text).

Cleaning rules:
- Keep ratings from **2010-01-01 to 2017-07-31**.
- Country = text before the first comma in `location` ("United States, Texas" → "United States").
- Merge England, Scotland, Wales and Northern Ireland into "United Kingdom".
- Drop users with no location. Drop duplicates.

What we know so far (2010–2017, users with a country): about 4.9 million ratings, 36,700 users, 23 countries
with at least 50 users. Norway has about 609 users and 184,000 ratings. Norwegians rate Norwegian beers far
more often than foreigners do, but give them about the same score as foreigners do.

## Experiment setup

**Target market:** Norway. **Source data:** all other countries.

Treat every rating as a positive interaction (the user tried the beer). The task is to rank beers the user
has not rated yet.

Norwegian users are split like this:
1. Use Norwegian users with at least 15 ratings as test users.
2. For each test user, sort ratings by date. Keep the **first 5** as known history.
3. The rest of their ratings are **hidden** and used only as the answer key.
4. Split test users 50/50 into validation (for tuning) and test (for final results). Fixed random seed.

No other Norwegian data is used in training. This copies a real new market: the app only knows the first
few ratings of its first Norwegian users.

**Never use hidden ratings for training, popularity counts, or any feature.**

## Models and runs

There are only two models: **popularity** and **BPR**. The runs use the same BPR code with different
training data, or with a small bonus added.

| Run | Method | Training data | Answers |
|---|---|---|---|
| Baseline | Most popular beers (count of ratings) | All other countries | Comparison point |
| B | BPR (`implicit` library) | All other countries | H1 |
| C | B + home-country bonus | Same as B | H2 |
| D *(if time)* | BPR | Nordic countries only (SE, DK, FI) | H3 |
| E *(if time)* | BPR | Random sample from all other non-Nordic countries, same number of ratings as D | H3 |

- All BPR runs also include the test users' first 5 ratings, so the model knows a little about each user.
- D and E must have the same amount of data, so the only difference is where the data comes from.
- Start with Baseline, B and C. Add D and E at the end if there is time.
- Do not recommend beers the user has already rated.
- Run C: `score = BPR score + w * (beer is from the user's country)`. Try w in {0, 0.1, 0.2, 0.5, 1.0}
  on the validation users and pick the best. If best w = 0, the home country does not help.
- Tune BPR settings on validation users only. Report final numbers on test users only.

## Evaluation

Metrics at K = 10 (binary relevance):
- **Recall@10:** share of a user's hidden beers that appear in their top 10.
- **NDCG@10:** like recall, but hits near the top count more.
- **Coverage@10:** share of all beers that appear in at least one top-10 list.

Report the number of test users. Run with a few random seeds and show the spread.

**Failure analysis:** Which test users get poor results? Look at number of ratings, favourite styles, and
how many of their hidden beers are Norwegian.

## Project structure

```
data/raw/         original files (not in git)
data/processed/   cleaned data (not in git)
notebooks/        01_data_overview, 02_split, 03_models, 04_results
src/              reusable code (data loading, split, models, metrics)
results/          tables and figures for the report
```

## Guidelines

- Python 3.11, pandas, numpy, implicit, matplotlib.
- Keep code simple and commented. Group members are not all programmers.
- Write all code, comments and output in English.
- Data files must never be committed.

## Limitations to mention in the report

- Country is a rough stand-in for culture.
- We do not know where a rating was made, only where the user lives and where the beer is brewed.
- Home-country effects may come from what is sold in each country, not only taste.
- Data is from 2010–2017 and mostly from Western countries.
- Most users are from the US.

## Reference

Lederrey, G., & West, R. (2018). When Sheep Shop: Measuring Herding Effects in Product Ratings with Natural
Experiments. *Proceedings of The Web Conference (WWW 2018)*.