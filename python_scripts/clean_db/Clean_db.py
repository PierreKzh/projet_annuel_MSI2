import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from general_processing.read_config_file import *
from general_processing.db_connection import *

def execute_sql_querry(cursor, sql_querry: str) -> None:
    """
    Execute an SQL query to update the database.

    Args:
    cursor: The database cursor used to execute the query.
    sql_querry (str): The SQL query to be executed.

    Returns:
    None
    """
    try:
        cursor.execute(sql_querry)
    except sqlite3.Error as e:
        print(f"Error sql querry {sql_querry}: {e}")

def fetch_all_data(cursor, query: str) -> List[Tuple]:
    """
    Fetch all rows from the database for the given query.

    Args:
    cursor: The database cursor used to execute the query.
    query (str): The SQL query to be executed.

    Returns:
    List[Tuple]: The rows fetched from the database.
    """
    try:
        cursor.execute(query)
        rows: List[Tuple] = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print(e)
        return []

def retention_time_func(cursor, traitement_size_block, retention_time):
    """
    Clean up old records in the database based on a time threshold.

    Args:
    cursor: The database cursor used to execute the queries.
    traitement_size_block: The size of the block of records to be processed.
    retention_time: The time threshold for keeping records.

    Returns:
    None
    """
    clean_image_classification_table = f"DELETE FROM Image_Classification WHERE packet_informations_id IN (SELECT packet_informations_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - {retention_time}) ORDER BY timestamp_input_in_db LIMIT {traitement_size_block});"
                                        # DELETE FROM Image_Classification WHERE packet_informations_id IN (SELECT packet_informations_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - 10) ORDER BY timestamp_input_in_db LIMIT 10);
    clean_packet_Informations_table = f"DELETE FROM Packet_Informations WHERE packet_data_id IN (SELECT packet_data_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - {retention_time}) ORDER BY timestamp_input_in_db LIMIT {traitement_size_block});"
                                       # DELETE FROM Packet_Informations WHERE packet_data_id IN (SELECT packet_data_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - 10) ORDER BY timestamp_input_in_db LIMIT 10);
    clean_packet_Data_table = f"DELETE FROM Packet_Data WHERE packet_data_id NOT IN (SELECT packet_data_id FROM Packet_Informations)"
                               # DELETE FROM Packet_Data WHERE packet_data_id NOT IN (SELECT packet_data_id FROM Packet_Informations)
    execute_sql_querry(cursor, clean_image_classification_table)
    execute_sql_querry(cursor, clean_packet_Informations_table)
    execute_sql_querry(cursor, clean_packet_Data_table)

def max_db_size_func(cursor, traitement_size_block):
    """
    Clean up records in the database to maintain the maximum database size.

    Args:
    cursor: The database cursor used to execute the queries.
    traitement_size_block: The size of the block of records to be processed.

    Returns:
    None
    """
    clean_image_classification_table = f"DELETE FROM Image_Classification WHERE packet_informations_id IN (SELECT packet_informations_id FROM Packet_Informations ORDER BY timestamp_input_in_db LIMIT {traitement_size_block});"
                                        # DELETE FROM Image_Classification WHERE packet_informations_id IN (SELECT packet_informations_id FROM Packet_Informations ORDER BY timestamp_input_in_db LIMIT 10);
    clean_packet_Informations_table = f"DELETE FROM Packet_Informations WHERE packet_data_id IN (SELECT packet_data_id FROM Packet_Informations ORDER BY timestamp_input_in_db LIMIT {traitement_size_block});"
                                       # DELETE FROM Packet_Informations WHERE packet_data_id IN (SELECT packet_data_id FROM Packet_Informations ORDER BY timestamp_input_in_db LIMIT 10);
    clean_packet_Data_table = f"DELETE FROM Packet_Data WHERE packet_data_id NOT IN (SELECT packet_data_id FROM Packet_Informations);"
                               # DELETE FROM Packet_Data WHERE packet_data_id NOT IN (SELECT packet_data_id FROM Packet_Informations);

    execute_sql_querry(cursor, clean_image_classification_table)
    execute_sql_querry(cursor, clean_packet_Informations_table)
    execute_sql_querry(cursor, clean_packet_Data_table)

def is_data_to_clean_retention_time(cursor, traitement_size_block, retention_time) -> bool:
    """
    Check if there is data to clean based on the time threshold.

    Args:
    cursor: The database cursor used to execute the queries.
    traitement_size_block: The size of the block of records to be processed.
    retention_time: The time threshold for keeping records.

    Returns:
    bool: True if there is data to clean, False otherwise.
    """
    data_to_clean = f"SELECT packet_informations_id FROM Packet_Informations WHERE timestamp_input_in_db <= (strftime('%s', 'now') - {retention_time}) ORDER BY timestamp_input_in_db LIMIT {traitement_size_block};"
    all_data_to_clean: List[Tuple] = fetch_all_data(cursor, data_to_clean)
    return len(all_data_to_clean) < int(traitement_size_block)

def is_max_db_size(db_file: str, max_db_size: float) -> bool:
    """
    Check if the database size exceeds the maximum allowed size.

    Args:
    db_file (str): The path to the database file.
    max_db_size (float): The maximum allowed size for the database in kilobytes.

    Returns:
    bool: True if the database size exceeds the maximum allowed size, False otherwise.
    """
    file_size_bytes = os.path.getsize(db_file)  # Get the size of the file in bytes
    file_size_kb = file_size_bytes / 1024  # Convert the file size to kilobytes
    return file_size_kb > max_db_size  # Compare the file size with the max_db_size (true or false)

def main() -> None:
    """
    Main function to clean the database based on configuration parameters.

    Returns:
    None
    """
    db_file = read_config_file("INITIALISATION", "OutputDBFile")
    traitement_size_block = read_config_file("CLEAN_DB", "TraitementSizeBlock")
    retention_time = read_config_file("CLEAN_DB", "RetentionTime")
    max_db_size = read_config_file("CLEAN_DB", "MaxDBSize")
    time_between_clean_request = read_config_file("CLEAN_DB", "TimeBetweenCleanRequest")
    time_between_clean_check = read_config_file("CLEAN_DB", "TimeBetweenCleanCheck")
    
    if '.' in max_db_size:
        max_db_size = float(max_db_size)
    elif max_db_size != '' :
        max_db_size = int(max_db_size)

    if '.' in time_between_clean_request:
        time_between_clean_request = float(time_between_clean_request)
    elif time_between_clean_request != '' :
        time_between_clean_request = int(time_between_clean_request)
    
    if '.' in time_between_clean_check:
        time_between_clean_check = float(time_between_clean_check)
    elif time_between_clean_check != '' :
        time_between_clean_check = int(time_between_clean_check)

    connection: Optional[sqlite3.Connection] = create_connection(db_file)  # Database connection
    cursor = connection.cursor()

    if connection:
        if retention_time != '' and max_db_size != '': # both option in file.conf
            while True: 
                loop_retention_time = is_data_to_clean_retention_time(cursor, traitement_size_block, retention_time)
                loop_max_db_size = is_max_db_size(db_file, max_db_size)
                if loop_retention_time == True or loop_max_db_size == True:
                    retention_time_func(cursor, traitement_size_block, retention_time)
                    max_db_size_func(cursor, traitement_size_block)
                    connection.commit()
                    time.sleep(time_between_clean_request)
                else:
                    time.sleep(time_between_clean_check)
        elif retention_time != '': # option RetentionTime set in file.conf
            while True:
                loop = is_data_to_clean_retention_time(cursor, traitement_size_block, retention_time)
                if loop == True:
                    retention_time_func(cursor, traitement_size_block, retention_time)
                    connection.commit()
                    time.sleep(time_between_clean_request)
                else:
                    time.sleep(time_between_clean_check)
        elif max_db_size != '': # option MaxDBSize set in file.conf
            while True:
                loop = is_max_db_size(db_file, max_db_size)
                if loop == True:
                    max_db_size_func(cursor, traitement_size_block)
                    connection.commit()
                    time.sleep(time_between_clean_request)
                else:
                    time.sleep(time_between_clean_check)
        
    connection.close()


if __name__ == "__main__":
    main()
