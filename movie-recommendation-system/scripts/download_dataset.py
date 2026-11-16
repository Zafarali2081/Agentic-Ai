"""
Script: download_dataset.py
Purpose: Downloads the official MovieLens dataset from GroupLens and extracts it to data/raw/
"""

import os
import sys
import zipfile
import urllib.request
from pathlib import Path

# Fix path to load config
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.append(str(PROJECT_ROOT / "backend"))

from config import RAW_DATA_DIR

sys.stdout.reconfigure(encoding="utf-8")

MOVIELENS_100K_URL = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"
MOVIELENS_LATEST_SMALL_URL = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"


def download_file(url: str, dest_path: Path):
    print(f"[*] Downloading {url} -> {dest_path}...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response, open(dest_path, "wb") as out_file:
        data = response.read()
        out_file.write(data)
    print(f"[+] Download complete: {dest_path} ({len(data)} bytes)")


def extract_zip(zip_path: Path, extract_to: Path):
    print(f"[*] Extracting {zip_path} -> {extract_to}...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"[+] Extraction complete.")


def main():
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = RAW_DATA_DIR / "ml-100k.zip"
    extracted_folder = RAW_DATA_DIR / "ml-100k"

    if extracted_folder.exists() and (extracted_folder / "u.data").exists():
        print(f"[OK] MovieLens 100K already exists in {extracted_folder}.")
        return

    try:
        download_file(MOVIELENS_100K_URL, zip_path)
        extract_zip(zip_path, RAW_DATA_DIR)
        print("[OK] MovieLens 100K dataset is ready for preprocessing.")
    except Exception as e:
        print(f"[!] Error downloading ml-100k: {e}. Attempting fallback to ml-latest-small...")
        fallback_zip = RAW_DATA_DIR / "ml-latest-small.zip"
        download_file(MOVIELENS_LATEST_SMALL_URL, fallback_zip)
        extract_zip(fallback_zip, RAW_DATA_DIR)
        print("[OK] MovieLens latest-small dataset is ready for preprocessing.")


if __name__ == "__main__":
    main()
