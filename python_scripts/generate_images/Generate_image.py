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
        # Comment or remove the next line to suppress the message
        # print("SQLite connection established to", output_db_file)
    except sqlite3.Error as e:
        print(e)
    return connection

def fetch_all_data(connection: sqlite3.Connection, query: str) -> List[Tuple]:
    """Fetch all rows from the database for the given query."""
    cursor = connection.cursor()
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
    """Convert a string of space-separated values into a scaled and normalized 23x23 numpy array."""
    elements: np.ndarray = np.genfromtxt(values_str.split(), dtype=float)
    if elements.size == 0:
        raise ValueError("No valid data found in the input string.")
    
    min_val: float = elements.min()
    shift: float = 1 - min_val if min_val <= 0 else 0
    shifted_values: np.ndarray = elements + shift + 1e-10  # Adding a small value to ensure positivity
    compressed_values: np.ndarray = np.log1p(shifted_values)
    min_val, max_val = compressed_values.min(), compressed_values.max()
    normalized_values: np.ndarray = np.uint8(
        255 * (compressed_values - min_val) / (max_val - min_val) if max_val > min_val else np.full_like(compressed_values, 128))
    return np.pad(normalized_values, (0, max(0, 529 - normalized_values.size)), 'constant')[:529].reshape((23, 23))

def process_data(packet_data: str, information_id: int, connection: Optional[sqlite3.Connection]) -> None:
    """Process a single packet data string and save it as an image in the database."""
    image_data: np.ndarray = convert_and_scale_values(packet_data)
    img: Image = Image.fromarray(image_data, 'L')
    img_base64: str = image_to_base64(img)
    
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Image_Classification (information_id, image_b64, classification)
            VALUES (?, ?, ?)
            """, (information_id, img_base64, ''))
        connection.commit()

def main() -> None:
    """Main function to process packet data and generate images."""
    read_config_file()

    # SQL statement for querying all data from Packet_Data table
    sql_query_packet_data: str = "SELECT * FROM Packet_Data;"

    # Create a database connection
    connection: Optional[sqlite3.Connection] = create_connection()

    # Fetch and process all data from Packet_Data if connection is successful
    if connection:
        all_data: List[Tuple] = fetch_all_data(connection, sql_query_packet_data)
        for row in all_data:
            processed_row: str = str(row).replace("'NULL'", "-1").replace(",", "").replace("(", "").replace(")", "").replace("None", "-1")
            row_elements: List[str] = processed_row.split()
            row_elements = row_elements[3:]  # Extract relevant elements
            while len(row_elements) < 513:
                row_elements.append('-1')
            processed_data: str = " ".join(row_elements)
            information_id: int = 123456789  # Replace with actual information ID if available
            process_data(processed_data, information_id, connection)
    else:
        print("Error! Cannot create the database connection.")

    connection.close()

if __name__ == '__main__':
    main()
