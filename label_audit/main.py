from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

import config
from src.auditor import run_audit
from src.data import filter_audit_set, load_example_products
from src.llm import LLMClient
from src.output import print_summary, write_results


def main() -> None:
    df = load_example_products(config.DATA_DIR)
    audit_set = filter_audit_set(df, config.TARGET_QUERIES)
    print(f"Audit set size: {len(audit_set)} rows")

    client = LLMClient(model=config.MODEL_NAME, prompt_path=config.PROMPT_PATH)
    results = run_audit(audit_set, client)

    path = write_results(results, config.OUTPUT_DIR)
    print(f"Results written to {path}\n")
    print_summary(results)


if __name__ == "__main__":
    main()
