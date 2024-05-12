import sqlite3
import configparser
import os

output_db_file = ""

def read_config_file():
    config_file = configparser.ConfigParser()
    global output_db_file

    current_folder = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_folder, "../file.conf")

    config_file.read(config_file_path)
    output_db_file = config_file.get('INITIALISATION', 'OutputDBFile')

def create_db():
    connection = sqlite3.connect(output_db_file)
    c = connection.cursor()

    # Table Packet_informations
    c.execute("""
    CREATE TABLE IF NOT EXISTS Packet_informations
    (
    [packet_id] INTEGER PRIMARY KEY,
    [forward_packets_per_second] INTEGER,
    [backward_packets_per_second] INTEGER,
    [bytes_transferred_per_second] INTEGER,
    [separator_1] INTEGER,
    [source_port] INTEGER,
    [destination_port] INTEGER,
    [ip_length] INTEGER,
    [payload_length] INTEGER,
    [ip_ttl] INTEGER,
    [ip_tos] INTEGER,
    [tcp_data_offset] INTEGER,
    [tcp_flags] INTEGER,
    [separator_2] INTEGER,
    [payload_bytes] TEXT
    )
    """)

    connection.commit()
    connection.close()

if __name__ == "__main__":
    read_config_file()
    create_db()
