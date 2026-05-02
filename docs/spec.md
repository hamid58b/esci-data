# ESCI Label Audit — Specification

## Problem Statement

The KDD Cup 2022 ESCI dataset defines label **"E" (Exact)** as:
> *"The item is relevant for the query and satisfies all the query specifications."*

In practice, some query-product pairs are mislabeled "E" — the product explicitly contradicts a requirement in the query (e.g., a query requesting "without pillow shams" paired with a product that includes them).

This project audits all "E"-labeled pairs for three target queries, flags mislabeled ones, and reformulates the query to correctly describe an "exact match" for those products.

**Target queries:**
- `aa batteries 100 pack`
- `kodak photo paper 8.5 x 11 glossy`
- `dewalt 8v max cordless screwdriver kit, gyroscopic`

---

## Ambiguity Rules (from task definition)

| Situation | Decision |
|---|---|
| Product info does not mention a spec in the query | Leave as "E" |
| Product has additional items/info beyond what was requested | Leave as "E" |
| Product explicitly contradicts a spec in the query | Flag as mislabeled → reformulate query |

---

## Folder Hierarchy

```
esci-data/                              ← repo root (existing)
├── docs/
│   └── spec.md                         ← this file
│
├── label_audit/                        ← all new project code lives here
│   ├── notebooks/
│   │   └── audit.ipynb                 ← explore → develop prompt → run → analyze
│   │
│   ├── src/
│   │   ├── __init__.py
│   │   ├── data.py                     ← load & filter df_example_products
│   │   ├── llm.py                      ← OpenAI client wrapper (model config)
│   │   ├── auditor.py                  ← core audit logic: calls LLM, parses result
│   │   └── output.py                   ← format and write results table
│   │
│   ├── prompts/
│   │   └── audit.txt                   ← full LLM prompt template (external file)
│   │
│   ├── output/                         ← generated results land here (gitignored)
│   │   └── .gitkeep
│   │
│   ├── config.py                       ← model name, target queries, column names
│   ├── main.py                         ← end-to-end runner (CLI entry point)
│   └── requirements.txt                ← project-specific deps
│
└── shopping_queries_dataset/           ← existing data (unchanged)
```

---

## Data Pipeline

### Step 1 — Build `df_example_products`

Merge the two parquet files exactly as described in the repo README:

```
df_examples  ← shopping_queries_dataset_examples.parquet
df_products  ← shopping_queries_dataset_products.parquet

df_example_products = LEFT JOIN on (product_locale, product_id)
```

### Step 2 — Filter to audit scope

```
Filter:  query IN target_queries
         AND esci_label == "E"
         AND product_locale == "us"
```

This produces the working set. Expected size: O(tens to low hundreds) of rows.

### Step 3 — Per-row LLM audit

For each row, pass the following context to the LLM:
- `query`
- `product_title`
- `product_description`
- `product_bullet_point`

The LLM returns a structured response (JSON):
```json
{
  "accurate": true | false,
  "reformulated_query": "<string or null>"
}
```

`accurate: true` means the "E" label is correct.  
`accurate: false` means the label is wrong; `reformulated_query` is the corrected query.

### Step 4 — Assemble output table

| Column | Source |
|---|---|
| `query_id` | from dataset |
| `product_id` | from dataset |
| `label_accurate` | LLM decision |
| `reformulated_query` | LLM output (null when `label_accurate=true`) |

Write to `output/results.csv`.

---

## LLM Design

**Model:** `gpt-4o-mini` (configurable via `config.py`)

**Prompt location:** `prompts/audit.txt`  
The prompt is loaded from disk at runtime — never hardcoded in Python.

**Prompt structure (defined in `audit.txt`):**
1. Role: expert search relevance assessor
2. Task definition + the three ambiguity rules (verbatim from spec)
3. Input schema (query, product fields)
4. Output schema: JSON only, no explanation outside the JSON
5. Few-shot example: one accurate "E" case, one mislabeled case with reformulation

**Calling strategy:** One LLM call per query-product pair. No batching needed at this scale. Temperature = 0 for determinism.

**Parsing:** Expect raw JSON in the response body. Validate with `pydantic` or simple `json.loads`. Retry once on parse failure.

---

## Module Responsibilities

### `config.py`
- `MODEL_NAME`: `"gpt-4o-mini"`
- `TARGET_QUERIES`: list of three query strings
- `DATA_DIR`: path to `shopping_queries_dataset/`
- `OUTPUT_DIR`: path to `output/`
- `PROMPT_PATH`: path to `prompts/audit.txt`

### `src/data.py`
- `load_example_products(data_dir) -> pd.DataFrame` — merge and return full joined frame
- `filter_audit_set(df, queries) -> pd.DataFrame` — apply scope filter

### `src/llm.py`
- `LLMClient(model, prompt_path)` — holds the OpenAI client and loaded prompt
- `audit_pair(query, product_fields) -> dict` — single call, returns parsed JSON dict
- Handles retry on parse error (max 1 retry)

### `src/auditor.py`
- `run_audit(df, llm_client) -> pd.DataFrame` — iterates rows, calls `llm_client.audit_pair`, collects results

### `src/output.py`
- `write_results(df, output_dir)` — writes `results.csv`
- `print_summary(df)` — prints counts to stdout

### `main.py`
End-to-end runner:
```
1. Load config
2. Build df_example_products, filter to audit set
3. Instantiate LLMClient
4. Run audit
5. Write results + print summary
```

Usage:
```bash
cd label_audit
python main.py
```

---

## Notebooks Plan

Notebooks are for exploration and validation — **not** for production use. Each notebook imports from `src/` once the modules exist.

| Notebook | Purpose |
|---|---|
| `audit.ipynb` | Single end-to-end notebook covering: data loading & schema inspection, sample row review, prompt development & iteration against a subset, full audit run, and results analysis with mislabeled rows displayed side-by-side. |

**Recommended workflow:**

1. Work through `audit.ipynb` top-to-bottom: explore data, tune the prompt, run the audit, review results
2. Once the prompt is locked, `python main.py` reproduces the full run headlessly

---

## Engineering Standards

- All public functions have type annotations; no docstrings (names are self-documenting)
- `src/` modules are independent and importable without side effects
- Prompt is never interpolated with f-strings in the template file; placeholders use `{query}`, `{product_title}`, etc., substituted at runtime with `.format(**kwargs)`
- No global state; config values are passed explicitly to constructors and functions
- `output/` is gitignored
- API key via `OPENAI_API_KEY` environment variable — never in code or config

---

## Dependencies (`label_audit/requirements.txt`)

```
pandas
pyarrow          # parquet support
openai           # OpenAI Python SDK
pydantic         # response validation
python-dotenv    # .env support for API key
```
