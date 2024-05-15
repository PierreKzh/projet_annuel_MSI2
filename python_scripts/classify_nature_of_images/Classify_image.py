import os
import pandas as pd
from tensorflow.keras.models import load_model  # type: ignore
from tensorflow.keras.preprocessing.image import img_to_array  # type: ignore
import sqlite3
import configparser
from typing import Optional, Tuple, List
import base64
from io import BytesIO
from PIL import Image
import numpy as np

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0 = all messages, 1 = no INFO, 2 = no INFO/WARNING, 3 = no INFO/WARNING/ERROR

output_db_file: str = ""

def read_config_file() -> None:
    """Read configuration from a file and update the global variable for database file path."""
    config: configparser.ConfigParser = configparser.ConfigParser()
    global output_db_file

    current_folder: str = os.path.dirname(os.path.abspath(__file__))
    config_file_path: str = os.path.join(current_folder, "../file.conf")  # Define path to the config file

    config.read(config_file_path)
    output_db_code: str = 'INITIALISATION'  # Section for initialization settings in config
    db_file_key: str = 'OutputDBFile'  # Key for database file configuration
    output_db_file = config.get(output_db_code, db_file_key)  # Read database file path from config

def create_connection(db_file: str) -> Optional[sqlite3.Connection]:
    """Create a connection to the SQLite database specified by db_file."""
    connection: Optional[sqlite3.Connection] = None
    try:
        connection = sqlite3.connect(db_file)
        print("SQLite connection established to", db_file)
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

def base64_to_image(base64_str: str) -> Image:
    """
    Convert a base64 string to a PIL Image.

    Args:
    base64_str (str): The base64 encoded string of the image.

    Returns:
    Image: The PIL Image object.
    """
    image_data = base64.b64decode(base64_str)
    buffered = BytesIO(image_data)
    img = Image.open(buffered)
    return img

def prepare_test_data(base64_str: str) -> np.ndarray:
    img = base64_to_image(base64_str)
    img = img.resize((32, 32))
    
    # Convert image to RGB if it's not
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array = img_array / 255.0  # Normalize
    return img_array

def classify_image(model, img_array: np.ndarray) -> dict:
    # Perform predictions on the image
    predictions = model.predict(img_array, verbose=0)
    prediction = predictions.flatten()[0]

    result = {
        'predicted_value': prediction,
        'prediction_result': 'Abnormal' if prediction > 0.5 else 'Normal'
    }

    return result

def update_classification(connection: sqlite3.Connection, image_classification_id: int, classification: str, classification_value: str) -> None:
    """Update the classification of an image in the database."""
    cursor = connection.cursor()
    update_query = "UPDATE Image_Classification SET classification = ?, classification_value = ? WHERE image_classification_id = ?"
    try:
        cursor.execute(update_query, (classification, classification_value, image_classification_id))
        connection.commit()
        #print(f"Updated image_classification_id {image_classification_id} with classification {classification}")
    except sqlite3.Error as e:
        print(f"Error updating classification for image_classification_id {image_classification_id}: {e}")

def main() -> None:
    read_config_file()
    model_path = "models/model-039.keras"
    
    # Load the model once outside of the loop
    model = load_model(model_path)
    
    # SQL statement for querying all data from Image_Classification table
    sql_query_packet_data: str = "SELECT image_classification_id, image_b64 FROM Image_Classification;"
    
    # Create a database connection
    connection: Optional[sqlite3.Connection] = create_connection(output_db_file)

    # Fetch and print all data from Image_Classification if connection is successful
    if connection:
        all_data: List[Tuple] = fetch_all_data(connection, sql_query_packet_data)
        for row in all_data:
            image_classification_id, base64_image = row  # Extract image_classification_id and base64 string from tuple
            
            test_data = prepare_test_data(base64_image)
            result = classify_image(model, test_data)

            classification = result['prediction_result']
            classification_value = str(result['predicted_value'])
            update_classification(connection, image_classification_id, classification, classification_value)

if __name__ == "__main__":
    main()
