from pathlib import Path

import pandas as pd


def load_example_products(data_dir: Path) -> pd.DataFrame:
    examples = pd.read_parquet(data_dir / "shopping_queries_dataset_examples.parquet")
    products = pd.read_parquet(data_dir / "shopping_queries_dataset_products.parquet")
    return pd.merge(
        examples,
        products,
        how="left",
        on=["product_locale", "product_id"],
    )


def filter_audit_set(df: pd.DataFrame, queries: list[str]) -> pd.DataFrame:
    mask = (
        df["query"].str.lower().isin([q.lower() for q in queries])
        & (df["esci_label"] == "E")
        & (df["product_locale"] == "us")
    )
    return df[mask].reset_index(drop=True)
