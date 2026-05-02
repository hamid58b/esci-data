# ESCI Label Audit

Identifies mislabeled "E" (Exact match) query-product pairs in the ESCI dataset using GPT-4o-mini, and reformulates the query for any pair that doesn't truly satisfy the exact-match definition.

## Setup

```bash
cd label_audit
pip install -r requirements.txt
```

**API key** — create a `.env` file at the repo root (one level above this folder):

```
OPENAI_API_KEY=sk-...
```

`find_dotenv()` in `main.py` walks up the directory tree automatically, so the key is found regardless of where you run from, as long as `.env` exists anywhere above `label_audit/`.

## Run

```bash
# from the label_audit/ directory
python3 main.py
```

Output is written to `label_audit/output/results.csv`.

## Notebook

For interactive exploration and prompt development:

```bash
cd label_audit/notebooks
jupyter notebook audit.ipynb
```

The notebook covers data exploration, prompt iteration, full audit run, and results analysis — all in one place.

## Output columns

| Column | Description |
|---|---|
| `query_id` | Query identifier |
| `product_id` | Product identifier |
| `label_accurate` | `True` if the "E" label is correct, `False` if mislabeled |
| `reformulated_query` | Corrected query when mislabeled, blank otherwise |

## Configuration

All tuneable parameters are in `config.py`: model name, target queries, and file paths. The prompt is in `prompts/audit.txt` — edit it there to adjust LLM behavior.
