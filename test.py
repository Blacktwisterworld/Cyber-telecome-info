import json
import duckdb

from config import HF_BASE_URL, RANGES_FILE


def main():
    print("Loading file_ranges.json...")

    with open(RANGES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    files = data["files"]

    print(f"Total files: {len(files)}")
    print("Connecting to first Parquet file...")

    first_file = files[0]["file"]
    parquet_url = HF_BASE_URL + first_file

    con = duckdb.connect(":memory:")

    try:
        result = con.execute(
            """
            SELECT
                COUNT(*) AS rows,
                MIN(CAST(mobile AS VARCHAR)) AS min_mobile,
                MAX(CAST(mobile AS VARCHAR)) AS max_mobile
            FROM read_parquet(?, hive_partitioning=false)
            """,
            [parquet_url]
        ).fetchone()

        print("File:", first_file)
        print("Rows:", result[0])
        print("Min mobile:", result[1])
        print("Max mobile:", result[2])
        print("TEST PASSED")

    finally:
        con.close()


if __name__ == "__main__":
    main()
