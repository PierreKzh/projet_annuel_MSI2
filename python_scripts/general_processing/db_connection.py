import sqlite3
from typing import Optional, Tuple, List

def create_connection(db) -> Optional[sqlite3.Connection]:
    """Create a connection to the SQLite database specified by output_db_file."""
    connection: Optional[sqlite3.Connection] = None
    try:
        connection = sqlite3.connect(db)
    except sqlite3.Error as e:
        print(e)
    return connection