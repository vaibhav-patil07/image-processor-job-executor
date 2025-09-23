import psycopg
from urllib.parse import urlparse, parse_qs


def get_pg_connection(db_url: str):
    """
    Create a psycopg2 connection from a PostgreSQL URL compatible with PgBouncer.
    
    Args:
        db_url (str): PostgreSQL connection URL, e.g.
            "postgresql://user:password@host:port/dbname"
    
    Returns:
        psycopg2.connection: Active connection object
    """
    # Parse URL
    parsed = urlparse(db_url)
    
    if parsed.scheme not in ("postgresql", "postgres"):
        raise ValueError("Invalid URL scheme, must be postgresql://")
    
    # Extract query parameters if any
    query_params = parse_qs(parsed.query)

    # Build connection parameters for psycopg2
    conn_params = {
        "dbname": parsed.path.lstrip("/"),
        "user": parsed.username,
        "password": parsed.password,
        "host": parsed.hostname,
        "port": parsed.port or 5432,
    }

    # Optional SSL handling (PgBouncer may not support sslmode in transaction pooling)
    if "sslmode" in query_params:
        conn_params["sslmode"] = query_params["sslmode"][0]

    # Create connection
    conn = psycopg.connect(**conn_params)
    return conn

class ImageModel:
    def __init__(self, db_url: str):
        try:
            # Clean the database URL to remove unsupported parameters
            self.conn = get_pg_connection(db_url)
            self.cursor = self.conn.cursor()
            print("Database connection established successfully")
        except psycopg.Error as e:
            print(f"Database connection error: {e}")
            raise e


    def get_image_by_id(self, image_id: str):
        self.cursor.execute("SELECT * FROM images WHERE image_id = %s", (image_id,))
        return self.cursor.fetchone()
    def updateImageJobStatus(self, image_id: str, status: str):
        self.cursor.execute("UPDATE images SET job_status = %s WHERE image_id = %s", (status, image_id))
        self.conn.commit()