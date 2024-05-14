import os
import pandas as pd
from tensorflow.keras.models import load_model  # type: ignore
from tensorflow.keras.preprocessing.image import ImageDataGenerator  # type: ignore
from dotenv import load_dotenv
import time

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0 = all messages, 1 = no INFO, 2 = no INFO/WARNING, 3 = no INFO/WARNING/ERROR
#os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' # I tensorflow/core/util/port.cc:113] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.

load_dotenv()

def prepare_test_data(IMG_TEST_PATH: str) -> ImageDataGenerator:
    # Generate file names from the directory
    filenames: list[str] = [f for f in os.listdir(IMG_TEST_PATH) if os.path.isfile(os.path.join(IMG_TEST_PATH, f))]
    test_labels: pd.DataFrame = pd.DataFrame({
        'image_name': filenames,  # Image names
        'full_path': [os.path.join(IMG_TEST_PATH, f) for f in filenames]  # Full path of images
    })

    # Initialize image generator with normalization
    test_datagen: ImageDataGenerator = ImageDataGenerator(rescale=1./255)
    
    # Configure the generator to read images directly from the DataFrame without a separate directory
    test_generator = test_datagen.flow_from_dataframe(
        dataframe=test_labels,
        directory=None,
        x_col='full_path',
        y_col=None,
        target_size=(32, 32),
        batch_size=128, # à selectionner en fonction de la puissance qu'on a 
        class_mode=None,
        shuffle=False)

    return test_generator

def classify_images(model_path: str, test_generator: ImageDataGenerator) -> None:
    # Load the model from the specified path
    model = load_model(model_path)

    # Perform predictions on the images
    predictions = model.predict(test_generator)
    predictions = predictions.flatten()

    # Store classification results in a DataFrame
    results: pd.DataFrame = pd.DataFrame({
        'image_name': [os.path.basename(f) for f in test_generator.filenames],
        'predicted_value': predictions,
        'prediction_result': ['Abnormal' if x > 0.5 else 'Normal' for x in predictions]
    })

    # Path where results will be saved
    csv_file_path: str = 'classification_results.csv'
    if os.path.exists(csv_file_path):
        # If existing CSV is detected, remove it before saving new results
        os.remove(csv_file_path)

    results.to_csv(csv_file_path, index=False)
    print("Classification results are saved in 'classification_results.csv'")

    # Calculate and display the number of 'Normal' and 'Abnormal' predictions
    count_normal: int = sum(results['prediction_result'] == 'Normal')
    count_abnormal: int = sum(results['prediction_result'] == 'Abnormal')
    print("Number of Normal:", count_normal)
    print("Number of Abnormal:", count_abnormal)

def main() -> None:
    start_time = time.time()

    BASE_PATH: str = os.getenv('PATH_ROOT_FOLDER')
    IMG_TEST_PATH: str = os.path.join(BASE_PATH, 'DATA/data_test/malicious_ack_tcp_dos_img')
    
    print("Preparing test data")
    test_generator = prepare_test_data(IMG_TEST_PATH)

    MODEL_PATH: str = os.path.join(BASE_PATH, 'models/model-045.keras')
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"The specified model does not exist: {MODEL_PATH}")

    print("Classifying images")
    classify_images(MODEL_PATH, test_generator)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()
