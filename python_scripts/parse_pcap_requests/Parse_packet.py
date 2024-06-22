from scapy.all import rdpcap, IP, TCP, sniff, get_if_addr, PacketList, Packet
import configparser
import os
import sqlite3
import time

output_db_file = ""
input_pcap_file = ""
network_interface = ""
capture_pcap_mode = 0
packets = PacketList()
packet_data_dict = {"timestamp_capture_packet": [], "forward_packets_per_second": [], "backward_packets_per_second": [], "bytes_transferred_per_second": [], "separator_1": [], "source_port": [], "destination_port": [], "ip_length": [], "payload_length": [], "ip_ttl": [], "ip_tos": [], "tcp_data_offset": [], "tcp_flags": [], "separator_2": [], "payload_bytes": []}
packet_informations_dict = {"packet_data_id": [], "timestamp_input_in_db": [], "capture_interface_file": []}
valid_packets_counter = 0

def create_sql_connection() -> sqlite3.Connection:
    """
    Create a connection to the SQLite database specified by output_db_file.

    Returns:
        sql_connection (sqlite3.Connection): sql connection to the db
    """
    try:
        sql_connection = sqlite3.connect(output_db_file)
    except Exception as e:
        print("Error connecting to the db", e)
        return 1
    
    return sql_connection

def execute_sql_query(cursor: sqlite3.Cursor, sql_payload: str) -> None:
    """
    Execute sql query from connection cursor and payload.

    Args:
        cursor (sqlite3.Cursor): sql cursor from connection
        sql_payload (str): sql query to execute
    """
    try:
        cursor.execute(sql_payload)
    except Exception as e:
        print("Error during the sql execution:", e)
        return 1

def load_pcap_file() -> None:
    """
    Load list of packets from a pcap file
    """
    global packets
    
    try:
        packets = rdpcap(input_pcap_file)
    except Exception as e:
        print("Error opening pcap file:", e)
        return 1

def parse_flow_information() -> None:
    """
    Parse the flow information category from packets following the network-packet-flow-header-payload dataset.
    Then fill the packet_data_dict with the corrects fields.
    """
    forward_packets_per_second = 0
    backward_packets_per_second = 0
    bytes_transferred_per_second = 0

    # variables definition
    if capture_pcap_mode == 0:
        current_ip = get_if_addr(network_interface)
        for pkt in packets:
            if IP in pkt:
                bytes_transferred_per_second += len(pkt)
                if pkt[IP].src == current_ip:
                    forward_packets_per_second += 1
                elif pkt[IP].dst == current_ip:
                    backward_packets_per_second += 1
    elif capture_pcap_mode == 1:
        # fake values if file
        forward_packets_per_second = 1190
        backward_packets_per_second = 1582
        bytes_transferred_per_second = 3542198

    # variables insertion
    for _ in range(valid_packets_counter):
        packet_data_dict["forward_packets_per_second"].append(forward_packets_per_second)
        packet_data_dict["backward_packets_per_second"].append(backward_packets_per_second)
        packet_data_dict["bytes_transferred_per_second"].append(bytes_transferred_per_second)

def parse_header_information(pkt: Packet) -> None:
    """
    Parse the header information category from packets following the network-packet-flow-header-payload dataset.
    Then fill the packet_data_dict with the corrects fields.

    Args:
        pkt (Packet): TCP/IP packet to parse
    """
    ip_length = pkt[IP].len
    ip_ttl = pkt[IP].ttl
    ip_tos = pkt[IP].tos
    source_port = pkt[TCP].sport
    destination_port = pkt[TCP].dport
    tcp_data_offset = pkt[TCP].dataofs
    tcp_flags = pkt[TCP].flags
    payload_length = len(pkt[TCP].payload)
    timestamp = pkt.time

    packet_data_dict["source_port"].append(source_port)
    packet_data_dict["destination_port"].append(destination_port)
    packet_data_dict["ip_length"].append(ip_length)
    packet_data_dict["payload_length"].append(payload_length)
    packet_data_dict["ip_ttl"].append(ip_ttl)
    packet_data_dict["ip_tos"].append(ip_tos)
    packet_data_dict["tcp_data_offset"].append(tcp_data_offset)
    packet_data_dict["tcp_flags"].append(int(tcp_flags))
    packet_data_dict["timestamp_capture_packet"].append(timestamp)

def parse_payload_bytes(pkt: Packet) -> None:
    """
    Parse the payload bytes category from packets following the network-packet-flow-header-payload dataset.
    Then fill the packet_data_dict with the corrects fields.

    Args:
        pkt (Packet): TCP/IP packet to parse
    """
    payload_bytes = ""
    payload = pkt[TCP].payload

    for byte in bytes(payload):
        payload_bytes += f"{str(byte)} "
    payload_bytes = payload_bytes[:-1]

    packet_data_dict["payload_bytes"].append(payload_bytes)

def fill_packet_informations(ids_table) -> None:
    """
    Fill the packet_informations_dict with the corrects fields
    """
    # Get current time
    timestamp_now = time.time()

    for id in ids_table:
        packet_informations_dict["packet_data_id"].append(id)
        packet_informations_dict["timestamp_input_in_db"].append(timestamp_now)
        if capture_pcap_mode == 0:
            packet_informations_dict["capture_interface_file"].append(network_interface)
        elif capture_pcap_mode == 1:
            packet_informations_dict["capture_interface_file"].append(input_pcap_file)

def write_dict_to_sqli(table_name: str, table_dict: dict) -> list:
    """
    Create an 'insert into' sql query from fields in dict to specific sql table.
    Then execute the sql query to the db.

    Args:
        table_name (str): Name of the sql table
        table_dict (dict): dict of sql table fields
    
    Returns:
        ids (list): Table of ids from packets inserted in the db
    """
    ids = []
    error_code = 0

    # Connect to db and execute sql payload
    connection = create_sql_connection()
    cursor = connection.cursor()

    # Create sql query
    max_values = max(len(values) for values in table_dict.values()) # get the maximum numbers of value from any columns in dict
    columns = list(table_dict.keys())
    for j in range(max_values):
        sql_payload = f"INSERT INTO {table_name} ("
        for i, column_name in enumerate(columns):  # get dict keys
            if i < len(columns) - 1:  # if not the last
                sql_payload += f"{column_name},"
            else:
                sql_payload += f"{column_name}) VALUES "
        sql_payload += "("
        for i, column in enumerate(columns):
            value = f"'{table_dict[column][j]}'"
            if i < len(columns) - 1:
                sql_payload += f"{value},"
            else:
                sql_payload += f"{value});"
        
        sql_return_code = execute_sql_query(cursor, sql_payload)
        if sql_return_code == 1:
            error_code = 1
        id = cursor.lastrowid
        ids.append(id)

    connection.commit()
    connection.close()

    return ids, error_code

def read_config_file() -> None:
    """
    Read the config file and get variables.
    """
    global output_db_file
    global input_pcap_file
    global network_interface
    global capture_pcap_mode
    config_file = configparser.ConfigParser()

    # Get config file path
    current_folder = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_folder, "../file.conf")

    # Get variables
    try:
        config_file.read(config_file_path)
    except Exception as e:
        print("Error reading config file:", e)
        return 1
    section = "PARSE_PCAP_REQUESTS"
    output_db_file = config_file.get('INITIALISATION', 'OutputDBFile')
    input_pcap_file = config_file.get(section, 'InputPCAPFile')
    network_interface = config_file.get(section, 'NetworkInterface')
    capture_pcap_mode = int(config_file.get(section, 'CapturePCAPMode'))

def sniff_network_interface() -> None:
    """
    Sniff network interface to fill packets list during one second.
    """
    global packets
    
    try:
        packets = sniff(iface=network_interface, timeout=1)
    except Exception as e:
        print("Error sniffing network:", e)
        return 1

def clear_dict(table_dict: dict) -> None:
    """
    Clear each tables in the fields of a dict.

    Args:
        table_dict (dict): dict of sql table fields
    """
    for field in table_dict.values():
        field.clear()

def packets_processing() -> None:
    """
    Clear temp stockage dict.
    Parse and count valid packets following the network-packet-flow-header-payload dataset.
    first, parse header information and payload bytes because they need informations from packets.
    Second, parse flow information because it need to calculate an average from packets.
    Third, parse packets informations because it use the same data for each packets.
    Fill temp stockage dict from packets parsed.
    Write dict_data to the db then write dict_informations to the db to link both tables.
    """
    global valid_packets_counter

    clear_dict(packet_informations_dict)
    clear_dict(packet_data_dict)
    valid_packets_counter = 0

    for packet in packets:
        if IP in packet:
            if TCP in packet:
                # filter valid packets
                valid_packets_counter += 1
                packet_data_dict["separator_1"].append(-1)
                parse_header_information(packet)
                packet_data_dict["separator_2"].append(-1)
                parse_payload_bytes(packet)

    if valid_packets_counter != 0:
        parse_flow_information() # calculate an average from packets
        ids, return_code = write_dict_to_sqli("Packet_Data", packet_data_dict)
        fill_packet_informations(ids) # same data for each packets
        if return_code != 1: # if no error in previous sql query
            write_dict_to_sqli("Packet_Informations", packet_informations_dict)

def main() -> None:
    """
    Start the program by chosing between reading a pcap file or listening on a network interface.
    """
    read_config_file()

    if capture_pcap_mode == 0: # sniff network
        while True:
            # loop each one second
            sniff_network_interface()
            packets_processing()
    elif capture_pcap_mode == 1: # read pcap
        load_pcap_file()
        packets_processing()

if __name__ == "__main__":
    main()
