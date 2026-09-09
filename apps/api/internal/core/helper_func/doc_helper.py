from internal.core.db import get_db_connection
def create_uploaded_document(
    title: str,
    original_filename: str,
    file_path: str,
    file_size: int,
    status: str = "PENDING"
) -> int:
    """Inserts a record into the uploaded_documents table and returns the inserted ID."""
    query = """
        INSERT INTO uploaded_documents (title, original_filename, file_path, file_size, status)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (title, original_filename, file_path, file_size, status))
            doc_id = cur.fetchone()[0]
            conn.commit()
            return doc_id
