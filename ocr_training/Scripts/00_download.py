# ocr_training/scripts/00_download.py
import subprocess, zipfile, os, pathlib

root = pathlib.Path(__file__).resolve().parents[1] / "data" / "handwritten_rx"
root.mkdir(parents=True, exist_ok=True)

# 1. download
subprocess.run(["kaggle", "datasets", "download",
                "-d", "mamun1113/doctors-handwritten-prescription-bd-dataset",
                "-p", str(root)], check=True)

# 2. unzip
for z in root.glob("*.zip"):
    with zipfile.ZipFile(z) as zf:
        zf.extractall(root)
    z.unlink()           # delete .zip after extraction
print("Done →", root)
