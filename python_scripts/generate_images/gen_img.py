import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # 0 = all messages, 1 = no INFO, 2 = no INFO/WARNING, 3 = no INFO/WARNING/ERROR --> pas de warning tensorflow
import time
from pathlib import Path
from typing import Tuple
import numpy as np
from PIL import Image
from tqdm.auto import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

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

def process_row(row: pd.Series, root_folder: Path) -> None:
    """
    Process a single row of dataset and save it as an image in the appropriate directory.

    Args:
    row (pd.Series): The dataset row containing the data.
    root_folder (Path): The root directory for saving the image.
    """
    # Check if 'attack_cat' column exists, if not use root_folder
    if 'attack_cat' in row and pd.notna(row['attack_cat']):
        folder_path: Path = root_folder / row['attack_cat']
    else:
        folder_path: Path = root_folder

    # Ensure the directory exists
    folder_path.mkdir(parents=True, exist_ok=True)
    
    # Convert packet data to image and save
    image_data: np.ndarray = convert_and_scale_values(row['packet_dat'])
    img: Image = Image.fromarray(image_data, 'L')
    img.save(folder_path / f"{row.name}.png")

def process_dataset(stage: str, clean: bool, path_data: str) -> None:
    """
    Process the dataset by converting each row to an image and saving it.

    Args:
    stage (str): The stage of the dataset (e.g., 'test', 'train').
    clean (bool): Whether to clean the directory before processing.
    dataset (str): The path to the dataset file.
    """
    data: str = f"{path_data}/{stage}.csv"
    img_folder: Path = Path(f"{path_data}/{stage}_img")
    df: pd.DataFrame = pd.read_csv(data)

    if clean:
        clean_directories(img_folder)

    # Prepare arguments for each task (translated comment)
    tasks: list = [(row, img_folder) for _, row in df.iterrows()]

    # Initialize the progress bar (translated comment)
    pbar = tqdm(total=len(tasks), desc=f"Processing {stage} dataset")

    with ProcessPoolExecutor() as executor:
        # Submit all tasks (translated comment)
        futures = [executor.submit(process_row, *task) for task in tasks]

        # Wait for each future to finish and update the progress bar (translated comment)
        for _ in as_completed(futures):
            pbar.update(1)

    pbar.close()

def user_confirmation(stage: str) -> Tuple[bool, bool]:
    """
    Request user confirmation to generate images for a specific stage and whether to clean the directory.

    Args:
    stage (str): The stage of the dataset (e.g., 'test', 'train').

    Returns:
    Tuple[bool, bool]: A tuple containing the user's response to generate images and whether to clean the directory.
    """
    response: str = input(f"Do you want to generate images for {stage}? (yes/no): ").lower()
    clean: bool = False
    if response == "yes" or response == "y":
        clean = input(f"Do you want to clean the {stage}_img folder first? (yes/no): ").lower() == "yes"
    return response == "yes" or response == "y", clean

def choose_directory(main_path) -> str:
    """
    Allows the user to choose a directory within a specified main path, recursing into subdirectories if no CSV files are found.
    """
    current_path = f"{main_path}/DATA"

    while True:
        try:
            # List directories and files in the current path
            entries = os.listdir(current_path)
            directories = [entry for entry in entries if os.path.isdir(os.path.join(current_path, entry))]
            files = [file for file in entries if file.endswith('.csv')]

            if files:
                # CSV files found, return the current path
                return current_path
            elif not directories:
                # No more directories to explore
                print("Reached a directory without CSV files and no further subdirectories.")
                return None

            # Show available directories
            print("Available directories:")
            for index, directory in enumerate(directories, 1):
                print(f"{index}. {directory}")

            # Ask for user selection
            selected_index = int(input("Choose a directory (enter number): ")) - 1
            if selected_index < 0 or selected_index >= len(directories):
                print("Invalid selection. Try again.")
                continue

            # Update the current path based on the selection and recurse into it
            current_path = os.path.join(current_path, directories[selected_index])

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

def main() -> None:
    """
    Main function to process the dataset based on user inputs.
    """
    main_path = os.getenv('PATH_ROOT_FOLDER')
    path_data = choose_directory(main_path)
    csv_files = [file[:-4] for file in os.listdir(path_data) if file.endswith('.csv')]
    stages: dict[str, bool] = {}
    
    for stage in csv_files:
        generate: bool
        clean: bool
        generate, clean = user_confirmation(stage)
        if generate:
            stages[stage] = clean

    start_time: float = time.time()
    for stage, clean in stages.items():
        process_dataset(stage, clean, path_data)

    print(f"Processing completed in {time.time() - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
