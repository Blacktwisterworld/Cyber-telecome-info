import duckdb
from config import HF_BASE_URL


def search_files(number, files):
    number = str(number)

    con = duckdb.connect(":memory:")

    try:
        for item in files:
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
                columns = [desc[0] for desc in con.description]

                return {
                    "file": file_path,
                    "data": dict(zip(columns, result))
                }

        return None

    finally:
        con.close()
