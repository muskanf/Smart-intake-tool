#!/usr/bin/env python3
"""
Concatenate all labels.csv files under handwritten_rx into master_labels.csv,
auto-detecting column names so we never crash on KeyError.
"""
import pandas as pd, pathlib, csv, sys, re

DATA_ROOT = pathlib.Path(__file__).resolve().parents[1] / "data" / "handwritten_rx"
csv_files = list(DATA_ROOT.rglob("labels.csv"))

if not csv_files:
    sys.exit(f"❌  No labels.csv files under {DATA_ROOT}")

rows = []
for csv_path in csv_files:
    df = pd.read_csv(csv_path)

    # --- find image column ---
    img_col_candidates = [c for c in df.columns if re.search(r"file|image", c, re.I)]
    img_col = img_col_candidates[0] if img_col_candidates else None

    # --- find label column ---
    lbl_col_candidates = [c for c in df.columns if re.search(r"label|drug", c, re.I)]
    lbl_col = lbl_col_candidates[0] if lbl_col_candidates else None

    # Walk rows
    for _, row in df.iterrows():
        # Path to image
        if img_col:
           img_path = csv_path.parent / "images" / row[img_col]
        else:  # fallback: look for *.png in same folder
            png = next(csv_path.parent.glob("*.png"))
            img_path = png

        # Drug text
        if lbl_col:
            drug = str(row[lbl_col])
        else:   # fallback: use parent folder or filename before underscore
            drug = (csv_path.parent.name if img_col is None
                    else re.split(r"[_/]", str(row[img_col]))[0])

        rows.append({"image": str(img_path.resolve()), "text": drug})

out_csv = DATA_ROOT / "master_labels.csv"
pd.DataFrame(rows).to_csv(out_csv, index=False, quoting=csv.QUOTE_MINIMAL)
print(f"✅  Wrote {out_csv} with {len(rows)} rows")
