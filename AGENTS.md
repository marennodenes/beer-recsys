# Code standard

Shared rules for the code in this project. Read `README.md` first to understand the task.
Applies to us and to our AI assistants (Claude Code and Codex).

## Main rules

1. **Use libraries where possible.** Don't write your own code for something a well-known library already does.
2. **Keep it simple.** Short, readable code is better than clever code.
3. **Never use the hidden Norwegian ratings** for training, popularity counts or features. Only for evaluation.
4. **Fixed random seed everywhere:** `SEED = 42`.
5. **Don't put data in git.** Everything under `data/` stays local.

## Folder structure

| Folder | What goes there |
|---|---|
| `data/raw/` | Original RateBeer files, downloaded by `setup_project.py`. Never edit these. |
| `data/processed/` | Cleaned data and our split, saved as `.parquet`. |
| `notebooks/` | Analysis and runs, numbered in order (see below). |
| `src/` | Reusable code that the notebooks import. |
| `results/` | Tables (`.csv`) and figures (`.png`) for the report. |

### Notebooks

| Notebook | Content |
|---|---|
| `01_data_overview.ipynb` | Load, clean and explore the data |
| `02_split.ipynb` | Create test/validation users and training data |
| `03_models.ipynb` | Popularity, BPR (run B) and home-country bonus (run C), optionally D and E |
| `04_results.ipynb` | Result tables, figures and failure analysis |

Notebooks should run in order from top to bottom.

### src/

| File | Content |
|---|---|
| `src/data.py` | Load and clean data (country from `location`, UK merge, date filter) |
| `src/split.py` | First 5 ratings as history, the rest hidden, 50/50 validation/test |
| `src/models.py` | Popularity baseline, BPR and home-country bonus |
| `src/metrics.py` | Recall@10, NDCG@10, Coverage@10 |

**Rule:** Logic used in more than one place goes in `src/`. Notebooks import and call the functions:

```python
from src.data import load_ratings
from src.metrics import recall_at_k
```

## Libraries

| Library | Used for |
|---|---|
| `pandas` | All tabular data |
| `numpy` | Numerical calculations |
| `scipy.sparse` | User × beer matrix for BPR |
| `implicit` | The BPR model (don't write your own BPR) |
| `matplotlib` / `seaborn` | Figures |
| `pyarrow` | Save/read `.parquet` |

- Everyone uses a virtual environment in `.venv/` (see Setup in `README.md`). Never install libraries outside it.
- All libraries must be listed in `requirements.txt`.
- Ask the group before adding a new library.
- Own code is only fine when no library fits well, e.g. our metrics in `src/metrics.py`.

## Style

- Code, variable names and comments in **English**.
- `snake_case` for variables and functions, `UPPER_CASE` for constants (`SEED`, `K = 10`).
- Descriptive names: `test_users`, not `df2`.
- Short functions that do one thing, with a one-line docstring:

  ```python
  def recall_at_k(recommended, hidden, k=10):
      """Share of the user's hidden beers found in the top k."""
  ```

- Comment *why*, not *what*.
- Use relative paths (`data/raw/ratings.txt.gz`), never `/Users/<name>/...`.

## Git

- `git pull` before you start working.
- Small commits with clear messages: `add popularity baseline`.
- Don't work in the same notebook as someone else at the same time. Tell the group who is working where.
- Don't commit large files, data or passwords.

## For AI assistants (Claude Code and Codex)

- Read `README.md` and this file before writing code.
- Follow the folder structure and libraries above. Don't create new folders or files without a reason.
- Explain briefly and simply what you did. The users are not programmers.
- Ask before making big changes, deleting files or adding libraries.
