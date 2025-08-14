from services.data_loader.dal import get_connection

def get_all_data():
    query = "SELECT * FROM data"
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

def run_sql_file(path: str) -> None:
    from pathlib import Path
    sql_text = Path(path).read_text(encoding="utf-8")
    with get_connection() as conn:
        conn.start_transaction()
        try:
            with conn.cursor() as cursor:
                for _ in cursor.execute(sql_text, multi=True):
                    pass
            conn.commit()
        except Exception:
            conn.rollback()
            raise

def create_table():
    run_sql_file("scripts/create_data.sql")

def insert_data():
    run_sql_file("scripts/insert_data.sql")