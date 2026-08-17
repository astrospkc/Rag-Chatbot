import os
import psycopg2
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    os.getenv(
        "DB_URL",
        "postgresql://postgres:postgres@localhost:5432/rag_db"
    )
)


def get_db_connection():
    """Establish and return a PostgreSQL connection with pgvector registered."""
    conn = psycopg2.connect(DATABASE_URL)
    register_vector(conn)
    return conn


def run_migrations():
    """Executes all SQL migration files in the migration directory."""
    migration_dir = os.path.join(os.path.dirname(__file__), "../../migration")
    sql_files = sorted([f for f in os.listdir(migration_dir) if f.endswith(".sql")])

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            for sql_file in sql_files:
                file_path = os.path.join(migration_dir, sql_file)
                with open(file_path, "r", encoding="utf-8") as f:
                    sql_script = f.read()
                    cur.execute(sql_script)
                print(f"Executed migration: {sql_file}")
    finally:
        conn.close()


# def insert_document(title: str, content: str, embedding: list[float]):
#     """Insert a document and its embedding into the documents table."""
#     with get_db_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute(
#                 """
#                 INSERT INTO documents (title, content, embedding)
#                 VALUES (%s, %s, %s)
#                 RETURNING id;
#                 """,
#                 (title, content, str(embedding))
#             )
#             doc_id = cur.fetchone()[0]
#             conn.commit()
#             return doc_id
