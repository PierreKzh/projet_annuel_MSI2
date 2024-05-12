import subprocess
import sys

def run_initialisation(path):
    """
    Executes a Python script located at the specified path.

    Args:
    path (str): The full path to the Python script to execute.

    Returns:
    int: The exit code of the process. A code of 0 indicates that the script completed without errors.
    """
    try:
        # Execute the Python script using subprocess
        subprocess.run([sys.executable, path], check=True, text=True, capture_output=True)
        print("Initialisation script executed successfully!")
    except subprocess.CalledProcessError as e:
        print("An error occurred during the initialisation script execution.")
        print("Error code:", e.returncode)
        print("Error message:", e.stderr)
        return e.returncode
    except Exception as e:
        print("Error during the subprocess execution:", str(e))
        return 1
    return 0

def run_parse_pcap_requests(path):
    """
    Executes a Python script located at the specified path.

    Args:
    path (str): The full path to the Python script to execute.

    Returns:
    int: The exit code of the process. A code of 0 indicates that the script completed without errors.
    """
    try:
        # Execute the Python script using subprocess
        subprocess.run([sys.executable, path], check=True, text=True, capture_output=True)
        print("Parse script executed successfully!")
    except subprocess.CalledProcessError as e:
        print("An error occurred during the parse script execution.")
        print("Error code:", e.returncode)
        print("Error message:", e.stderr)
        return e.returncode
    except Exception as e:
        print("Error during the subprocess execution:", str(e))
        return 1
    return 0

if __name__ == "__main__":
    script_path = r"python_scripts\Initialisation\create_sqlite_db.py"
    exit_code = run_initialisation(script_path)
    if exit_code != 0 :
        print(exit_code)

    script_path = r"python_scripts\parse_pcap_requests\convert_pcap_to_sqli.py"
    exit_code = run_parse_pcap_requests(script_path)
    if exit_code != 0 :
        print(exit_code)
