"""Download the full openFDA food enforcement dataset to data/enforcement.jsonl.

openFDA caps skip at 25,000, and the dataset has ~29k records, so we pull one report_date year at a time.
"""
import json
import os
import time
from datetime import date

import requests

BASE = "https://api.fda.gov/food/enforcement.json"
KEY = os.environ.get("OPENFDA_KEY")


def get(params, tries=5):
    for i in range(tries):
        r = requests.get(BASE, params=params, timeout=60)
        if r.status_code == 404:  # openFDA's "no results"
            return None
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(2 ** i)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError(f"openFDA failed after {tries} tries: {params}")


def fetch_year(year):
    rows, skip = [], 0
    while True:
        params = {"search": f"report_date:[{year}0101 TO {year}1231]", "limit": 1000, "skip": skip}
        if KEY:
            params["api_key"] = KEY
        data = get(params)
        if not data or not data.get("results"):
            break
        res = data["results"]
        rows.extend(res)
        skip += len(res)
        if len(res) < 1000:
            break
        time.sleep(0.3)
    return rows


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    seen, total = set(), 0
    with open("data/enforcement.jsonl", "w") as f:
        for year in range(2004, date.today().year + 1):
            rows = fetch_year(year)
            kept = 0
            for r in rows:
                k = json.dumps(r, sort_keys=True)
                if k in seen:
                    continue
                seen.add(k)
                f.write(k + "\n")
                kept += 1
            total += kept
            print(year, kept, flush=True)
    print("total records:", total)
