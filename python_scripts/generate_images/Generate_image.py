import os
import sqlite3
import configparser
import numpy as np
from PIL import Image
from io import BytesIO
import base64
from typing import Optional, Tuple, List

# Global variable for the database file path
output_db_file: str = ""

def read_config_file() -> None:
    """Read configuration from a file and update the global variable for database file path."""
    config = configparser.ConfigParser()
    global output_db_file

    current_folder = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_folder, "../file.conf")  # Define path to the config file

    config.read(config_file_path)
    output_db_code = 'INITIALISATION'  # Section for initialization settings in config
    db_file_key = 'OutputDBFile'  # Key for database file configuration
    output_db_file = config.get(output_db_code, db_file_key)  # Read database file path from config

def create_connection() -> Optional[sqlite3.Connection]:
    """Create a connection to the SQLite database specified by output_db_file."""
    connection: Optional[sqlite3.Connection] = None
    try:
        connection = sqlite3.connect(output_db_file)
    except sqlite3.Error as e:
        print(e)
    return connection

def fetch_all_data(cursor, query: str) -> List[Tuple]:
    """Fetch all rows from the database for the given query."""
    try:
        cursor.execute(query)
        rows: List[Tuple] = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print(e)
        return []

def image_to_base64(img: Image) -> str:
    """Convert a PIL Image to a base64 string."""
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

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

    cursor.execute("""
        INSERT INTO Image_Classification (packet_informations_id, image_b64, classification)
        VALUES (?, ?, ?)
        """, (packet_informations_id, img_base64, ''))
    
def update_treatement_progress(cursor, packet_data_id):
    cursor.execute("""
        UPDATE Packet_Informations
        SET treatment_progress = ?
        WHERE packet_data_id = ?
        """, (1, packet_data_id))

def get_packet_informations_id(cursor, packet_data_id):
    cursor.execute("""
        SELECT packet_informations_id
        FROM Packet_Informations
        WHERE packet_data_id = ?
        """, (packet_data_id,))
    packet_informations_id = cursor.fetchone()
    
    print(packet_informations_id)
    
    if packet_informations_id is not None:
        return packet_informations_id[0]
    else:
        print('eqùoifjzliefjlqezhfdlzqhefm:ksqhnekf:jhsqmefhzqmekhfmqoziehflzq')
        return "get_packet_informations_id Error"

def main() -> None:
    """Main function to process packet data and generate images."""
    read_config_file()

    # SQL statement for querying all data from Packet_Data table
    sql_query_packet_data: str = "SELECT * FROM Packet_Data WHERE packet_data_id IN (SELECT packet_data_id FROM Packet_Informations WHERE treatment_progress = 0 ORDER BY timestamp_input_in_db ASC LIMIT 10)"
    
    # Create a database connection
    connection: Optional[sqlite3.Connection] = create_connection()
    

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
