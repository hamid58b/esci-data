import pandas as pd

from .llm import LLMClient


def run_audit(df: pd.DataFrame, client: LLMClient) -> pd.DataFrame:
    records = []
    for _, row in df.iterrows():
        result = client.audit_pair(
            query=row["query"],
            product_title=row.get("product_title", ""),
            product_description=row.get("product_description", ""),
            product_bullet_point=row.get("product_bullet_point", ""),
        )
        records.append(
            {
                "query_id": row["query_id"],
                "product_id": row["product_id"],
                "label_accurate": result["accurate"],
                "reformulated_query": result["reformulated_query"],
            }
        )
    return pd.DataFrame(records)
