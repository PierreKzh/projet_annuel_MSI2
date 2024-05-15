from scapy.all import rdpcap, IP, TCP, sniff, get_if_addr
import configparser
import os
import sqlite3
from datetime import datetime

output_db_file = ""
input_pcap_file = ""
network_interface = ""
capture_pcap_mode = 0
packets = 0
packet_data_dict = {"forward_packets_per_second": [], "backward_packets_per_second": [], "bytes_transferred_per_second": [], "separator_1": [], "source_port": [], "destination_port": [], "ip_length": [], "payload_length": [], "ip_ttl": [], "ip_tos": [], "tcp_data_offset": [], "tcp_flags": [], "separator_2": [], "payload_bytes": []}
packet_informations_dict = {"timestamp_input_in_db": [], "capture_interface_file": []}

def load_pcap_file():
    global input_pcap_file
    global packets
    
    try:
        packets = rdpcap(input_pcap_file)
    except Exception as e:
        print("Error during opening pcap file:", e)
        return 1

def parse_flow_information():
    global capture_pcap_mode
    global network_interface
    global packets
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
    for pkt in packets:
        if IP in pkt:
            if TCP in pkt:
                packet_data_dict["forward_packets_per_second"].append(forward_packets_per_second)
                packet_data_dict["backward_packets_per_second"].append(backward_packets_per_second)
                packet_data_dict["bytes_transferred_per_second"].append(bytes_transferred_per_second)

def parse_header_information(pkt):
    ip_length = pkt[IP].len
    ip_ttl = pkt[IP].ttl
    ip_tos = pkt[IP].tos
    source_port = pkt[TCP].sport
    destination_port = pkt[TCP].dport
    tcp_data_offset = pkt[TCP].dataofs
    tcp_flags = pkt[TCP].flags
    payload_length = len(pkt[TCP].payload)

    packet_data_dict["source_port"].append(source_port)
    packet_data_dict["destination_port"].append(destination_port)
    packet_data_dict["ip_length"].append(ip_length)
    packet_data_dict["payload_length"].append(payload_length)
    packet_data_dict["ip_ttl"].append(ip_ttl)
    packet_data_dict["ip_tos"].append(ip_tos)
    packet_data_dict["tcp_data_offset"].append(tcp_data_offset)
    packet_data_dict["tcp_flags"].append(int(tcp_flags))

def parse_payload_bytes(pkt):
    payload_bytes = ""
    payload = pkt[TCP].payload

    for byte in bytes(payload):
        payload_bytes += f"{str(byte)} "
    payload_bytes = payload_bytes[:-1]

    packet_data_dict["payload_bytes"].append(payload_bytes)

def fill_packet_informations():
    global packets
    global capture_pcap_mode
    global network_interface
    global input_pcap_file

    # Get current time
    date_time_now = datetime.now()
    formatted_date_time = date_time_now.strftime("%Y-%m-%d %H:%M:%S")

    for packet in packets:
        if IP in packet:
            if TCP in packet:
                packet_informations_dict["timestamp_input_in_db"].append(formatted_date_time)
                if capture_pcap_mode == 0:
                    packet_informations_dict["capture_interface_file"].append(network_interface)
                elif capture_pcap_mode == 1:
                    packet_informations_dict["capture_interface_file"].append(input_pcap_file)

def create_sql_payload_from_dict(table_name, dict):
    sql_payload = ""

    max_values = max(len(values) for values in dict.values()) # get the maximum numbers of value from any columns in dict
    columns = list(dict.keys())

    sql_payload += f"INSERT INTO {table_name} ("
    for i, column_name in enumerate(columns):  # get dict keys
        if i < len(columns) - 1:  # if not the last
            sql_payload += f"{column_name},"
        else:
            sql_payload += f"{column_name}) VALUES "
    for k in range(max_values):
        sql_payload += "("
        for i, column in enumerate(columns):
            value = f"'{dict[column][k]}'"
            if i < len(columns) - 1:
                sql_payload += f"{value},"
            else:
                sql_payload += f"{value}"
        if k < max_values - 1:
            sql_payload += "),"
        else:
            sql_payload += "); "

    return sql_payload

def write_dict_to_sqli():
    global output_db_file
    sql_payload = ""

    # Complete sql payload for Packet_Data table
    sql_payload += create_sql_payload_from_dict("Packet_Data", packet_data_dict)

    # Complete sql payload for Packet_Informations table
    sql_payload += create_sql_payload_from_dict("Packet_informations", packet_informations_dict)

    # Connect to db and execute sql payload
    connection = sqlite3.connect(output_db_file)
    c = connection.cursor()
    
    try:
        c.executescript(sql_payload)
    except Exception as e:
        print("Error during the sql execution:", e)
        return 1

    connection.commit()
    connection.close()

def read_config_file():
    config_file = configparser.ConfigParser()
    global output_db_file
    global input_pcap_file
    global network_interface
    global capture_pcap_mode

    current_folder = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_folder, "../file.conf")

    config_file.read(config_file_path)
    section = "PARSE_PCAP_REQUESTS"
    output_db_file = config_file.get('INITIALISATION', 'OutputDBFile')
    input_pcap_file = config_file.get(section, 'InputPCAPFile')
    network_interface = config_file.get(section, 'NetworkInterface')
    capture_pcap_mode = int(config_file.get(section, 'CapturePCAPMode'))

def sniff_network_interface():
    global network_interface
    global packets
    
    try:
        packets = sniff(iface=network_interface, timeout=1)
    except Exception as e:
        print("Error during :", e)
        return 1

def clear_dict(dict):
    for table in dict.values():
        table.clear()

def packets_processing():
    global packets

    for packet in packets:
        if IP in packet:
            if TCP in packet:
                packet_data_dict["separator_1"].append(-1)
                parse_header_information(packet)
                packet_data_dict["separator_2"].append(-1)
                parse_payload_bytes(packet)
    parse_flow_information()
    fill_packet_informations()

    write_dict_to_sqli()
    clear_dict(packet_informations_dict)
    clear_dict(packet_data_dict)

def main():
    read_config_file()

    if capture_pcap_mode == 0:
        while True:
            sniff_network_interface()
            packets_processing()
    elif capture_pcap_mode == 1:
        load_pcap_file()
        packets_processing()

if __name__ == "__main__":
    main()
