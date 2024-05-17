import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from general_processing.read_config_file import *
from general_processing.db_connection import *

def execute_sql_querry(cursor, sql_querry: str) -> None:
    """Update the classification of an image in the database."""
    try:
        cursor.execute(sql_querry)
    except sqlite3.Error as e:
        print(f"Error sql querry {sql_querry}: {e}")

def execute_cleaning_sql_commands(cursor, traitement_size_block, keep_time):
    
    #clean_image_classification_table = f"DELETE FROM Image_Classification WHERE packet_informations_id IN (SELECT packet_informations_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - {keep_time}) ORDER BY timestamp_input_in_db LIMIT {traitement_size_block});"
    #clean_packet_Informations_table = f"DELETE FROM Packet_Informations WHERE packet_data_id IN (SELECT packet_data_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - {keep_time}) ORDER BY timestamp_input_in_db LIMIT {traitement_size_block});"
    
    clean_packet_Informations_table = f"DELETE FROM Packet_Informations WHERE packet_data_id IN (SELECT packet_data_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - {keep_time}) ORDER BY timestamp_input_in_db LIMIT {traitement_size_block});"
    clean_image_classification_table = f"DELETE FROM Image_Classification WHERE packet_informations_id NOT IN (SELECT packet_informations_id FROM Packet_Informations)"
    clean_packet_Data_table = f"DELETE FROM Packet_Data WHERE packet_data_id NOT IN (SELECT packet_data_id FROM Packet_Informations)"

    execute_sql_querry(clean_packet_Informations_table)
    execute_sql_querry(clean_image_classification_table)
    execute_sql_querry(clean_packet_Data_table)

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
DELETE FROM Packet_Data WHERE packet_data_id NOT IN (SELECT packet_data_id FROM Packet_Informations)
"""