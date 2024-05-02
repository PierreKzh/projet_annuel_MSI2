from scapy.all import rdpcap, IP, TCP, sniff, get_if_addr
import configparser
import os
import sqlite3


output_db_file = ""
input_pcap_file = ""
network_interface = ""
capture_pcap_mode = 0
packets = 0
db_dict = {"forward_packets_per_second": [], "backward_packets_per_second": [], "bytes_transferred_per_second": [], "separator_1": [], "source_port": [], "destination_port": [], "ip_length": [], "payload_length": [], "ip_ttl": [], "ip_tos": [], "tcp_data_offset": [], "tcp_flags": [], "separator_2": [], "payload_bytes": []}


def load_pcap_file():
    global input_pcap_file
    global packets

    packets = rdpcap(input_pcap_file)


def parse_flow_information():
    global capture_pcap_mode
    global network_interface
    global packets
    forward_packets_per_second = 0
    backward_packets_per_second = 0
    bytes_transferred_per_second = 0

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
        forward_packets_per_second = 1190
        backward_packets_per_second = 1582
        bytes_transferred_per_second = 3542198

    max_values = max(len(values) for values in db_dict.values())
    for i in range(max_values):
        db_dict["forward_packets_per_second"].append(forward_packets_per_second)
        db_dict["backward_packets_per_second"].append(backward_packets_per_second)
        db_dict["bytes_transferred_per_second"].append(bytes_transferred_per_second)


def parse_header_information(pkt):
    ip_length = pkt[IP].len
    ip_ttl = pkt[IP].ttl
    ip_tos = pkt[IP].tos
    source_port = pkt[TCP].sport
    destination_port = pkt[TCP].dport
    tcp_data_offset = pkt[TCP].dataofs
    tcp_flags = pkt[TCP].flags
    payload_length = len(pkt[TCP].payload)

    db_dict["source_port"].append(source_port)
    db_dict["destination_port"].append(destination_port)
    db_dict["ip_length"].append(ip_length)
    db_dict["payload_length"].append(payload_length)
    db_dict["ip_ttl"].append(ip_ttl)
    db_dict["ip_tos"].append(ip_tos)
    db_dict["tcp_data_offset"].append(tcp_data_offset)
    db_dict["tcp_flags"].append(int(tcp_flags))


def parse_payload_bytes(pkt):
    payload_bytes = ""

    payload = pkt[TCP].payload

    for byte in bytes(payload):
        payload_bytes += f"{str(byte)} "

    db_dict["payload_bytes"].append(payload_bytes)


def write_dict_to_sqli():
    global output_db_file
    sql_payload = ""

    # Create sql payload
    max_values = max(len(values) for values in db_dict.values())
    columns = list(db_dict.keys())

    sql_payload += "INSERT INTO Packet_informations ("
    for i, column_name in enumerate(columns):  # récupère les keys du dict
        if i < len(columns) - 1:  # si ce n'est pas le dernier
            sql_payload += f"{column_name},"
        else:
            sql_payload += f"{column_name}) VALUES "
    for k in range(max_values):
        sql_payload += "("
        for i, column in enumerate(columns):  # récupère les keys du dict
            value = f"'{db_dict[column][k]}'"
            if i < len(columns) - 1:  # si ce n'est pas le dernier
                sql_payload += f"{value},"
            else:
                sql_payload += f"{value}"
        if k < max_values-1:
            sql_payload += "),"
        else:
            sql_payload += ")"

    # Connect to db and execute sql payload
    connection = sqlite3.connect(output_db_file)
    c = connection.cursor()

    c.execute(sql_payload)

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

    packets = sniff(iface=network_interface, timeout=1)


def packets_processing():
    global packets

    for packet in packets:
        if IP in packet:
            if TCP in packet:
                db_dict["separator_1"].append(-1)
                parse_header_information(packet)
                db_dict["separator_2"].append(-1)
                parse_payload_bytes(packet)
    parse_flow_information()

    write_dict_to_sqli()


if __name__ == "__main__":
    read_config_file()

    if capture_pcap_mode == 0:
        while True:
            sniff_network_interface()
            packets_processing()
    elif capture_pcap_mode == 1:
        load_pcap_file()
        packets_processing()
