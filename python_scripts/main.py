import subprocess
import sys

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

def main():
    print("init.py")
    init_script_path = r"python_scripts\Initialisation\init.py"
    exit_code = execute_python_script(init_script_path)
    if exit_code != 0:
        print(exit_code)

    print("Parse_packet.py")
    parse_script_path = r"python_scripts\parse_pcap_requests\Parse_packet.py"
    exit_code = execute_python_script(parse_script_path)
    if exit_code != 0:
        print(exit_code)

    """print("Generate_image.py")
    parse_script_path = r"python_scripts\generate_images\Generate_image.py"
    exit_code = execute_python_script(parse_script_path)
    if exit_code != 0:
        print(exit_code)

    print("Classify_image.py")
    parse_script_path = r"python_scripts\classify_nature_of_images\Classify_image.py"
    exit_code = execute_python_script(parse_script_path)
    if exit_code != 0:
        print(exit_code)"""
    


if __name__ == "__main__":
    main()
