import os
import time
from pathlib import Path
import numpy as np
from PIL import Image
from tqdm.auto import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
import argparse
import base64
from io import BytesIO
import sqlite3
from typing import Optional, Tuple, List
import configparser

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

def image_to_base64(img: Image) -> str:
    """
    Convert a PIL Image to a base64 string.

    Args:
    img (Image): The PIL Image object.

    Returns:
    str: The base64 encoded string of the image.
    """
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
    if elements.size == 0:
        raise ValueError("No valid data found in the input string.")
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

def process_data(packet_data: str, information_id: int) -> None:
    """
    Process a single packet data string and save it as an image in the specified directory.

    Args:
    packet_data (str): The packet data string containing space-separated values.
    output_folder (Path): The directory for saving the image.
    image_name (str): The name for the saved image.
    """
    
    # Convert packet data to image and save to db
    image_data: np.ndarray = convert_and_scale_values(packet_data)
    img: Image = Image.fromarray(image_data, 'L')
    img_base64: str = image_to_base64(img)
    
    connection = create_connection(output_db_file)
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Image_Classification (information_id, image_b64, classification)
            VALUES (?, ?, ?)
            """, (information_id, img_base64, ''))
        connection.commit()
        connection.close()

def main() -> None:
    """
    Main function to process the dataset based on user inputs.
    """
    
    parser = argparse.ArgumentParser(description='Process packet data into an image and save to database.')
    parser.add_argument('data', type=str, help='The packet data string containing space-separated values.')
    parser.add_argument('information_id', type=int, help='The foreign key ID referencing the Packet_Informations table.')
    
    args = parser.parse_args()
    packet_data = args.data
    information_id = args.information_id

    process_data(packet_data, information_id)


if __name__ == "__main__":
    main()
