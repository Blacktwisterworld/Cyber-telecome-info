import duckdb
from config import HF_BASE_URL, RANGES_FILE
import json


def load_ranges():
    with open(RANGES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["files"]


def find_candidate_files(number):
    number = str(number)

    candidates = []

    for item in load_ranges():
        first = str(item["first"])
        last = str(item["last"])

        # Numeric comparison
        try:
            number_int = int(number)
            first_int = int(first)
            last_int = int(last)

            if first_int <= number_int <= last_int:
                candidates.append(item)

        except ValueError:
            continue

    return candidates


def search_files(number):
    number = str(number)

    # Step 1: JSON se candidate files nikalo
    candidates = find_candidate_files(number)

    if not candidates:
        return {
            "result": None,
            "candidates": [],
        }

    con = duckdb.connect(":memory:")

    try:
        # Step 2: Sirf candidate files me search karo
        for item in candidates:

            file_path = item["file"]
            parquet_url = HF_BASE_URL + file_path

            query = """
                SELECT *
                FROM read_parquet(?, hive_partitioning=false)
                WHERE CAST(mobile AS VARCHAR) = ?
                LIMIT 1
            """

            result = con.execute(
                query,
                [parquet_url, number]
            ).fetchone()

            if result:
                columns = [
                    description[0]
                    for description in con.description
                ]

                return {
                    "result": {
                        "file": file_path,
                        "data": dict(zip(columns, result)),
                    },
                    "candidates": candidates,
                }

        return {
            "result": None,
            "candidates": candidates,
        }

    finally:
        con.close()
