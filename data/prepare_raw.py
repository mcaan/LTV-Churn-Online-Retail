"""Convert the UCI Online Retail.xlsx download to the CSV expected by notebook 1."""
from pathlib import Path
import pandas as pd

folder = Path(__file__).resolve().parent / "raw"
source = folder / "Online Retail.xlsx"
target = folder / "Online Retail.csv"
if not source.is_file():
    raise FileNotFoundError(f"Download the UCI workbook and place it at {source}")
frame = pd.read_excel(source, engine="openpyxl")
frame.to_csv(target, index=False)
print(f"Saved {len(frame):,} rows to {target}")
