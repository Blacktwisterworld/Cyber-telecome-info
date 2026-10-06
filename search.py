import json
import duckdb

from config import HF_BASE_URL, RANGES_FILE


def load_file_ranges():
    """Load all file ranges from file_ranges.json."""

    with open(RANGES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data["files"]


def find_candidate_files(number):
    """
    Find ALL files whose first/last range contains the number.

    Condition:
        first <= number <= last
    """

    number = str(number)
    number_int = int(number)

    candidates = []

    for item in load_file_ranges():

        first = str(item["first"])
        last = str(item["last"])

        try:
            first_int = int(first)
            last_int = int(last)
        except ValueError:
            continue

        if first_int <= number_int <= last_int:
            candidates.append(item)

    return candidates


def search_files(number, progress_callback=None):
    """
    1. Find candidate files from JSON.
    2. Scan every candidate file one-by-one.
    3. Stop immediately when exact mobile match is found.
    """

    number = str(number)

    # -----------------------------------------
    # STEP 1: JSON RANGE CHECK
    # -----------------------------------------

    candidates = find_candidate_files(number)

    if not candidates:
        return {
            "result": None,
            "candidates": [],
        }

    # -----------------------------------------
    # STEP 2: SEARCH CANDIDATE PARQUET FILES
    # -----------------------------------------

    con = duckdb.connect(":memory:")

    try:

        for index, item in enumerate(candidates, start=1):

            file_path = item["file"]

            # Send progress information to Telegram
            if progress_callback:
                progress_callback(
                    index,
                    len(candidates),
                    file_path
                )

            parquet_url = HF_BASE_URL + file_path

            query = """
                SELECT *
                FROM read_parquet(
                    ?,
                    hive_partitioning=false
                )
                WHERE CAST(mobile AS VARCHAR) = ?
                LIMIT 1
            """

            result = con.execute(
                query,
                [parquet_url, number]
            ).fetchone()

            # -----------------------------------------
            # EXACT MATCH FOUND
            # -----------------------------------------

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
                    "checked": index,
                }

        # -----------------------------------------
        # NO MATCH IN ANY CANDIDATE FILE
        # -----------------------------------------

        return {
            "result": None,
            "candidates": candidates,
            "checked": len(candidates),
        }

    finally:
        con.close()
