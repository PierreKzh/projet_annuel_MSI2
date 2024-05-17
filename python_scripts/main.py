import subprocess
import sys
import threading
import time
import os

def execute_python_script(path: str) -> int:
    """
    Executes a Python script located at the specified path and handles exceptions.

    Args:
        path (str): The full path to the Python script to execute.

    Returns:
        int: The exit code of the process. A code of 0 indicates that the script completed without errors.
    """
    try:
        # Execute the Python script using subprocess
        result = subprocess.run([sys.executable, path], check=True, text=True, capture_output=True)
        print(f"Script executed successfully: {path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during the script execution at {path}.")
        print("Error code:", e.returncode)
        print("Error message:", e.stderr)
        return e.returncode
    except Exception as e:
        print(f"Error during the subprocess execution at {path}: {str(e)}")
        return 1
    return 0

def execute_with_delay(script_path: str, delay: int):
    """
    Executes a Python script after a specified delay.

    Args:
        script_path (str): The path to the Python script.
        delay (int): The delay in seconds before executing the script.
    """
    time.sleep(delay)
    exit_code = execute_python_script(script_path)
    if exit_code != 0:
        print(exit_code)

def main():
    
    file_path = "db.sqlite"

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Le fichier '{file_path}' a été supprimé avec succès.")
    else:
        print(f"Le fichier '{file_path}' n'existe pas.")

    print("init.py")
    init_script_path = r"python_scripts\Initialisation\init.py"
    exit_code = execute_python_script(init_script_path)
    if exit_code != 0:
        print(exit_code)
        return  # Exit if the initialization script fails

    print("Parse_packet.py")
    parse_script_path = r"python_scripts\parse_pcap_requests\Parse_packet.py"
    parse_thread = threading.Thread(target=execute_python_script, args=(parse_script_path,))
    parse_thread.start()
    #time.sleep(5)

    print("Generate_image.py")
    generate_image_script_path = r"python_scripts\generate_images\Generate_image.py"
    generate_thread = threading.Thread(target=execute_with_delay, args=(generate_image_script_path, 5))

    print("Classify_image.py")
    classify_image_script_path = r"python_scripts\classify_nature_of_images\Classify_image.py"
    classify_thread = threading.Thread(target=execute_with_delay, args=(classify_image_script_path, 5))

    # Start the threads for Generate_image.py and Classify_image.py
    generate_thread.start()
    classify_thread.start()

    # Wait for the threads to complete
    parse_thread.join()
    generate_thread.join()
    classify_thread.join()

if __name__ == "__main__":
    main()
