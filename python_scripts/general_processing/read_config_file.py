import configparser
import os

def read_config_file(section: str, key: str) -> str:
    """Read configuration from a file and update the global variable for database file path."""
    config: configparser.ConfigParser = configparser.ConfigParser()

    current_folder: str = os.path.dirname(os.path.abspath(__file__))
    config_file_path: str = os.path.join(current_folder, "../file.conf")  # Define path to the config file

    config.read(config_file_path)
    key_value: str = config.get(section, key)  # Read database file path from config

    return key_value