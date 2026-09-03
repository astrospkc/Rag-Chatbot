import os
import psycopg2
from dotenv import load_dotenv
from pgvector.psycopg2 import register_vector
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Base declarative class for SQLAlchemy ORM models
Base = declarative_base()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    os.getenv(
        "DB_URL",
        "postgresql://postgres:postgres@localhost:5432/rag_db"
    )
)

# Ensure SQLAlchemy connection string format (postgresql+psycopg2://)
SQLALCHEMY_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1) if DATABASE_URL.startswith("postgresql://") else DATABASE_URL

# SQLAlchemy Engine and SessionFactory
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI Dependency that yields a SQLAlchemy database session and ensures cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_connection():
    """Establish and return a raw PostgreSQL connection with pgvector registered (Psycopg2)."""
    conn = psycopg2.connect(DATABASE_URL)
    register_vector(conn)
    return conn


# def run_migrations():
#     """Executes all SQL migration files in the migration directory using raw psycopg2 connection."""
#     migration_dir = os.path.join(os.path.dirname(__file__), "../../migration")
#     if not os.path.exists(migration_dir):
#         return

#     sql_files = sorted([f for f in os.listdir(migration_dir) if f.endswith(".sql")])

#     conn = psycopg2.connect(DATABASE_URL)
#     conn.autocommit = True
#     try:
#         with conn.cursor() as cur:
#             for sql_file in sql_files:
#                 file_path = os.path.join(migration_dir, sql_file)
#                 with open(file_path, "r", encoding="utf-8") as f:
#                     sql_script = f.read()
#                     cur.execute(sql_script)
#                 print(f"Executed migration: {sql_file}")
#     finally:
#         conn.close()



