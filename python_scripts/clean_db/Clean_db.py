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
    
def keep_time_func(cursor, traitement_size_block, keep_time):
    clean_image_classification_table = f"DELETE FROM Image_Classification WHERE packet_informations_id IN (SELECT packet_informations_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - {keep_time}) ORDER BY timestamp_input_in_db LIMIT {traitement_size_block});"
    clean_packet_Informations_table = f"DELETE FROM Packet_Informations WHERE packet_data_id IN (SELECT packet_data_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - {keep_time}) ORDER BY timestamp_input_in_db LIMIT {traitement_size_block});"
    clean_packet_Data_table = f"DELETE FROM Packet_Data WHERE packet_data_id NOT IN (SELECT packet_data_id FROM Packet_Informations)"

    execute_sql_querry(cursor, clean_packet_Informations_table)
    execute_sql_querry(cursor, clean_image_classification_table)
    execute_sql_querry(cursor, clean_packet_Data_table)

def max_db_size_func(cursor, traitement_size_block):
    pass


def main() -> None:
    db_file = read_config_file("INITIALISATION", "OutputDBFile")
    traitement_size_block = read_config_file("CLEAN_DB", "TraitementSizeBlock")
    keep_time = read_config_file("CLEAN_DB", "KeepTime")
    max_db_size = read_config_file("CLEAN_DB", "MaxDBSize")

    connection: Optional[sqlite3.Connection] = create_connection(db_file) # Database connection
    cursor = connection.cursor()

    if connection:
        if keep_time != '' and max_db_size != '':
            while True:
                keep_time_func(cursor, traitement_size_block, keep_time)
                max_db_size_func(cursor, traitement_size_block)
                connection.commit()
        elif keep_time != '':
            while True:
                keep_time_func(cursor, traitement_size_block, keep_time)
                connection.commit()
        elif max_db_size != '':
            while True:
                max_db_size_func(cursor, traitement_size_block)
                connection.commit()
        
    connection.close()


if __name__ == "__main__":
    main()


"""
SELECT packet_informations_id, packet_data_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - 10) ORDER BY timestamp_input_in_db LIMIT 10

DELETE FROM Image_Classification WHERE packet_informations_id IN (SELECT packet_informations_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - 10) ORDER BY timestamp_input_in_db LIMIT 10);
DELETE FROM Packet_Informations WHERE packet_data_id IN (SELECT packet_data_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - 10) ORDER BY timestamp_input_in_db LIMIT 10);
DELETE FROM Packet_Data WHERE packet_data_id NOT IN (SELECT packet_data_id FROM Packet_Informations)
"""