import sqlite3
import configparser
import os
from typing import Optional

output_db_file: str = ""

def read_config_file() -> None:
    """Read configuration from a file and update the global variable for database file path."""
    config_file = configparser.ConfigParser()
    global output_db_file

    current_folder: str = os.path.dirname(os.path.abspath(__file__))
    config_file_path: str = os.path.join(current_folder, "../file.conf")  # Define path to the config file

    config_file.read(config_file_path)
    output_db_file = config_file.get('INITIALISATION', 'OutputDBFile')  # Read database file path from config

def create_connection(db_file: str) -> Optional[sqlite3.Connection]:
    """Create a connection to the SQLite database specified by db_file."""
    connection: Optional[sqlite3.Connection] = None
    try:
        connection = sqlite3.connect(db_file)
        print("SQLite connection established to", db_file)
    except sqlite3.Error as e:
        print(e)
    return connection

def create_table(connection: sqlite3.Connection, create_table_sql: str) -> None:
    """Create a table using the provided SQL statement."""
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_sql)
    except sqlite3.Error as e:
        print(e)

def main() -> None:
    read_config_file()

    # SQL statements for creating tables
    sql_create_packet_informations_table: str = """
    CREATE TABLE IF NOT EXISTS Packet_Informations (
        packet_informations_id INTEGER PRIMARY KEY AUTOINCREMENT,
        packet_data_id INTEGER,
        timestamp_imput_in_db INTEGER,
        capture_interface_file TEXT,
        treatment_progress INTEGER DEFAULT 0
        FOREIGN KEY(packet_data_id) REFERENCES Packet_Informations(packet_data_id)
    );
    """

    sql_create_image_classification_table: str = """
    CREATE TABLE IF NOT EXISTS Image_Classification (
        image_classification_id INTEGER PRIMARY KEY AUTOINCREMENT,
        packet_informations_id INTEGER,
        image_b64 TEXT,
        classification TEXT,
        FOREIGN KEY(packet_informations_id) REFERENCES Packet_Informations(packet_informations_id)
    );
    """

    sql_create_packet_data_table: str = """
    CREATE TABLE IF NOT EXISTS Packet_Data (
        packet_data_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp_capture_packet INTEGER,
        forward_packets_per_second INTEGER,
        backward_packets_per_second INTEGER,
        bytes_transferred_per_second INTEGER,
        separator_1 INTEGER,
        source_port INTEGER,
        destination_port INTEGER,
        ip_length INTEGER,
        payload_length INTEGER,
        ip_ttl INTEGER,
        ip_tos INTEGER,
        tcp_data_offset INTEGER,
        tcp_flags INTEGER,
        separator_2 INTEGER,
        payload_bytes INTEGER,
    );
    """

    # Create a database connection
    connection = create_connection(output_db_file)

    # Create tables if connection is successful
    if connection:
        create_table(connection, sql_create_packet_informations_table)
        create_table(connection, sql_create_image_classification_table)
        create_table(connection, sql_create_packet_data_table)
        print("Tables created successfully.")
        connection.close()
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
