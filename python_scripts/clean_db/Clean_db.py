import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from general_processing.read_config_file import *
from general_processing.db_connection import *

sql_query_packet_data: str = f"SELECT packet_informations_id, image_classification_id, image_b64 FROM Image_Classification WHERE packet_informations_id IN (SELECT packet_informations_id FROM Packet_Informations WHERE treatment_progress = 1 ORDER BY timestamp_input_in_db ASC LIMIT {traitement_size_block});"

def keep_time_func():
    pass

def max_db_size_func():
    pass

def main() -> None:
    db_file = read_config_file("INITIALISATION", "OutputDBFile")
    traitement_size_block = read_config_file("CLASSIFY_IMAGE", "TraitementSizeBlock")
    keep_time = read_config_file("CLASSIFY_IMAGE", "KeepTime")
    max_db_size = read_config_file("CLASSIFY_IMAGE", "MaxDBSize")

    connection: Optional[sqlite3.Connection] = create_connection(db_file) # Database connection
    cursor = connection.cursor()

    if connection:
        if keep_time != '':
            keep_time_func()
        if max_db_size != '':
            max_db_size_func()


if __name__ == "__main__":
    main()


"""
SELECT packet_informations_id, packet_data_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - 10) ORDER BY timestamp_input_in_db LIMIT 10

DELETE FROM Image_Classification WHERE packet_informations_id IN (SELECT packet_informations_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - 10) ORDER BY timestamp_input_in_db LIMIT 10);
DELETE FROM Packet_Informations WHERE packet_data_id IN (SELECT packet_data_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - 10) ORDER BY timestamp_input_in_db LIMIT 10);
DELETE FROM Packet_Data WHERE packet_informations_id IN (SELECT packet_informations_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - 10) ORDER BY timestamp_input_in_db LIMIT 10);
"""