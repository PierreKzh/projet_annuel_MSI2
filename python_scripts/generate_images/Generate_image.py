import os
import sqlite3
import numpy as np
from PIL import Image
from typing import Optional, Tuple, List
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from general_processing.read_config_file import *
from general_processing.b64_image import *
from general_processing.db_connection import *

def fetch_all_data(cursor, query: str) -> List[Tuple]:
    """Fetch all rows from the database for the given query."""
    try:
        cursor.execute(query)
        rows: List[Tuple] = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print(e)
        return []

def convert_and_scale_values(values_str: str) -> np.ndarray:
    """
    Convert a string of space-separated values into a scaled and normalized 23x23 numpy array.

    Args:
    values_str (str): The input string containing space-separated values.

    Returns:
    np.ndarray: A 23x23 numpy array of the processed values.
    """
    elements: np.ndarray = np.fromstring(values_str, sep=' ')
    min_val: float = elements.min()
    # Shift values if the minimum is less than or equal to 0
    shift: float = 1 - min_val if min_val <= 0 else 0
    shifted_values: np.ndarray = elements + shift
    # Compress values using logarithm
    compressed_values: np.ndarray = np.log1p(shifted_values)
    # Normalize values to the 0-255 range
    min_val, max_val = compressed_values.min(), compressed_values.max()
    normalized_values: np.ndarray = np.uint8(
        255 * (compressed_values - min_val) / (max_val - min_val) if max_val > min_val else np.full_like(compressed_values, 128))
    # Ensure the array is of size 529 (23x23) and reshape
    return np.pad(normalized_values, (0, max(0, 529 - normalized_values.size)), 'constant')[:529].reshape((23, 23))

def process_data(packet_data: str, packet_informations_id: int, cursor, ) -> None:
    """Process a single packet data string and save it as an image in the database."""
    image_data: np.ndarray = convert_and_scale_values(packet_data)
    img: Image = Image.fromarray(image_data, 'L')
    img_base64: str = image_to_base64(img)

    try:
        cursor.execute("""
            INSERT INTO Image_Classification (packet_informations_id, image_b64, classification)
            VALUES (?, ?, ?)
            """, (packet_informations_id, img_base64, ''))
    except sqlite3.Error as e:
        print(f"Error inserting generated image for packet_informations_id {packet_informations_id}: {e}")
    
def update_treatement_progress(cursor, packet_data_id):
    try:
        cursor.execute("""
            UPDATE Packet_Informations
            SET treatment_progress = ?
            WHERE packet_data_id = ?
            """, (1, packet_data_id))
    except sqlite3.Error as e:
        print(f"Error updating treatment_progress for packet_data_id {packet_data_id}: {e}")

def get_packet_informations_id(cursor, packet_data_id):
    try:
        cursor.execute("""
            SELECT packet_informations_id
            FROM Packet_Informations
            WHERE packet_data_id = ?
            """, (packet_data_id,))
    except sqlite3.Error as e:
        print(f"Error getting packet_informations_id for packet_data_id {packet_data_id}: {e}")
    packet_informations_id = cursor.fetchone()
    
    if packet_informations_id is not None:
        return packet_informations_id[0]
    else:
        print('eqùoifjzliefjlqezhfdlzqhefm:ksqhnekf:jhsqmefhzqmekhfmqoziehflzq')
        return "get_packet_informations_id Error"

def main() -> None:
    db_file = read_config_file("INITIALISATION", "OutputDBFile")
    traitement_size_block = read_config_file("GENERATE_IMAGE", "TraitementSizeBlock")

    # SQL statement for querying data from Packet_Data table
    sql_query_packet_data: str = f"SELECT * FROM Packet_Data WHERE packet_data_id IN (SELECT packet_data_id FROM Packet_Informations WHERE treatment_progress = 0 ORDER BY timestamp_input_in_db ASC LIMIT {traitement_size_block})" 
    
    connection: Optional[sqlite3.Connection] = create_connection(db_file) # Database connection
    
    if connection:
        cursor = connection.cursor()
        while True :
            all_data: List[Tuple] = fetch_all_data(cursor, sql_query_packet_data)
            for row in all_data:
                processed_row: str = str(row).replace("'NULL'", "-1").replace(",", "").replace("(", "").replace(")", "").replace("None", "-1").replace(" '", "").replace("'", "")
                processed_row: List[str] = processed_row.split()
                packet_data_id = processed_row[0]
                processed_row = processed_row[2:]  # Extract relevant elements
                while len(processed_row) < 513:
                    processed_row.append('-1')
                if len(processed_row) > 513:
                    processed_row = processed_row[:513]
                processed_row: str = " ".join(processed_row)
                packet_informations_id = get_packet_informations_id(cursor, packet_data_id)
                process_data(processed_row, packet_informations_id, cursor)
                update_treatement_progress(cursor, packet_data_id)
                connection.commit()
    else:
        print("Error! Cannot create the database connection.")

    connection.close()

if __name__ == '__main__':
    main()
