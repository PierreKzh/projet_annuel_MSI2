import os
from tensorflow.keras.models import load_model  # type: ignore
from tensorflow.keras.preprocessing.image import img_to_array  # type: ignore
import sqlite3
from typing import Optional, Tuple, List
from PIL import Image
import numpy as np
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from general_processing.read_config_file import *
from general_processing.b64_image import *
from general_processing.db_connection import *

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0 = all messages, 1 = no INFO, 2 = no INFO/WARNING, 3 = no INFO/WARNING/ERROR

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

def prepare_test_data(base64_str: str) -> np.ndarray:
    img: Image = base64_to_image(base64_str)
    img = img.resize((32, 32))
    
    # Convert image to RGB if it's not
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    img_array: np.ndarray = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array = img_array / 255.0  # Normalize
    return img_array

def classify_image(model, img_array: np.ndarray, normal_abnormal) -> dict:
    # Perform predictions on the image
    predictions: np.ndarray = model.predict(img_array, verbose=0)
    prediction: float = predictions.flatten()[0]

    result: dict = {
        'predicted_value': prediction,
        'prediction_result': 'Abnormal' if prediction > normal_abnormal else 'Normal'
    }

    return result

def update_classification(cursor, image_classification_id: int, classification: str, classification_value: str) -> None:
    """Update the classification of an image in the database."""
    update_query = "UPDATE Image_Classification SET classification = ?, classification_value = ? WHERE image_classification_id = ?"
    try:
        cursor.execute(update_query, (classification, classification_value, image_classification_id))
    except sqlite3.Error as e:
        print(f"Error updating classification for image_classification_id {image_classification_id}: {e}")

def update_treatement_progress(cursor, packet_informations_id):
    try:
        cursor.execute("""
            UPDATE Packet_Informations
            SET treatment_progress = ?
            WHERE packet_informations_id = ?
            """, (2, packet_informations_id))
    except sqlite3.Error as e:
        print(f"Error updating treatment_progress for packet_informations_id {packet_informations_id}: {e}")

def main() -> None:
    db_file = read_config_file("INITIALISATION", "OutputDBFile")
    model_path = read_config_file("CLASSIFY_IMAGE", "ModelPath")
    traitement_size_block = read_config_file("CLASSIFY_IMAGE", "TraitementSizeBlock")
    normal_abnormal = read_config_file("CLASSIFY_IMAGE", "NormalAbnormal")
    if '.' in normal_abnormal :
        normal_abnormal = float(normal_abnormal)
    else :
        normal_abnormal = int(normal_abnormal)

    model = load_model(model_path) # Load the model
    
    # SQL statement for querying data from Image_Classification table
    sql_query_packet_data: str = f"SELECT packet_informations_id, image_classification_id, image_b64 FROM Image_Classification WHERE packet_informations_id IN (SELECT packet_informations_id FROM Packet_Informations WHERE treatment_progress = 1 ORDER BY timestamp_input_in_db ASC LIMIT {traitement_size_block});"
    
    connection: Optional[sqlite3.Connection] = create_connection(db_file) # Database connection
    
    if connection:
        cursor = connection.cursor()
        while True :
            all_data: List[Tuple] = fetch_all_data(connection, sql_query_packet_data)
            for row in all_data:
                packet_informations_id, image_classification_id, base64_image = row  # Extract image_classification_id and base64 string from tuple
                
                test_data = prepare_test_data(base64_image)
                result = classify_image(model, test_data, normal_abnormal)

                classification = result['prediction_result']
                classification_value = str(result['predicted_value'])
                update_classification(cursor, image_classification_id, classification, classification_value)
                update_treatement_progress(cursor, packet_informations_id)
                connection.commit()

    connection.close()

if __name__ == "__main__":
    main()
