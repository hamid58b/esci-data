from pathlib import Path

import pandas as pd


def write_results(df: pd.DataFrame, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "results.csv"
    df.to_csv(path, index=False)
    return path


def print_summary(df: pd.DataFrame) -> None:
    total = len(df)
    mislabeled = (~df["label_accurate"]).sum()
    print(f"Total pairs audited : {total}")
    print(f"Accurate ('E' correct): {total - mislabeled}")
    print(f"Mislabeled           : {mislabeled}")
    if mislabeled:
        print("\nMislabeled rows:")
        cols = ["query_id", "product_id", "reformulated_query"]
        print(df[~df["label_accurate"]][cols].to_string(index=False))
