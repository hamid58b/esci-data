from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT.parent / "shopping_queries_dataset"
OUTPUT_DIR = ROOT / "output"
PROMPT_PATH = ROOT / "prompts" / "audit.txt"

MODEL_NAME = "gpt-5.4-mini"
TEMPERATURE = 0.0

TARGET_QUERIES = [
    "aa batteries 100 pack",
    "kodak photo paper 8.5 x 11 glossy",
    "dewalt 8v max cordless screwdriver kit, gyroscopic",
]
