import sqlite3
import configparser
import os
from typing import Optional, Tuple, List
import subprocess
import sys

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

def execute_python_script(path: str, arg1: str, arg2: str) -> int:
    """
    Executes a Python script located at the specified path with two arguments and handles exceptions.

    Args:
        path (str): The full path to the Python script to execute.
        arg1 (str): The first argument to pass to the script.
        arg2 (str): The second argument to pass to the script.

    Returns:
        int: The exit code of the process. A code of 0 indicates that the script completed without errors.
    """
    try:
        # Execute the Python script using subprocess with the two arguments
        result = subprocess.run([sys.executable, path, arg1, arg2], check=True, text=True, capture_output=True)
        print(f"Script executed successfully: {path}")
        print("Output:", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during the script execution at {path}.")
        print("Error code:", e.returncode)
        print("Error message:", e.stderr)
        return e.returncode
    except Exception as e:
        print(f"Error during the subprocess execution at {path}: {str(e)}")
        return 1
    return 0

def fetch_all_data(connection: sqlite3.Connection, query: str) -> List[Tuple]:
    """Fetch all rows from the database for the given query."""
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print(e)
        return []

def main() -> None:
    read_config_file()

    # SQL statement for querying all data from Packet_Data table
    sql_query_packet_data: str = """
    SELECT * FROM Packet_Data;
    """

    # Create a database connection
    connection = create_connection(output_db_file)

    # Fetch and print all data from Packet_Data if connection is successful
    if connection:
        all_data = fetch_all_data(connection, sql_query_packet_data)
        for row in all_data:
            row = str(row).replace("'NULL'", "-1").replace(",","").replace("(","").replace(")","").replace("None","-1")
            row = row.split()
            row = row[3:]
            while len(row) < 513:
                row.append('-1')
            row = " ".join(row)
            parse_script_path = r"python_scripts\generate_images\gen_img.py"
            exit_code = execute_python_script(parse_script_path, row, "123456789")
            if exit_code != 0:
                print(exit_code)
        connection.close()
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
