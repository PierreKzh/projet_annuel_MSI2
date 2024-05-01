from scapy.all import rdpcap, IP, TCP, sniff, get_if_addr
import configparser
import os

output_csv_file = ""
input_pcap_file = ""
network_interface = ""
capture_pcap_mode = 0
packets = 0

def load_pcap_file():
    global input_pcap_file
    global packets

    packets = rdpcap(input_pcap_file)


def parse_flow_information():
    global capture_pcap_mode
    global network_interface
    global packets
    forward_packet_per_second = 0
    backward_packet_per_second = 0
    bytes_transferred_per_second = 0

    if capture_pcap_mode == 0:
        current_ip = get_if_addr(network_interface)
        for pkt in packets:
            if IP in pkt:
                bytes_transferred_per_second += len(pkt)
                if pkt[IP].src == current_ip:
                    forward_packet_per_second += 1
                elif pkt[IP].dst == current_ip:
                    backward_packet_per_second += 1
        flow_information = [forward_packet_per_second, backward_packet_per_second, bytes_transferred_per_second]
    elif capture_pcap_mode == 1:
        flow_information = [1190, 1582, 3542198]

    return flow_information


def parse_header_information(pkt):
    header_information = []

    ip_length = pkt[IP].len
    ip_ttl = pkt[IP].ttl
    ip_tos = pkt[IP].tos
    source_port = pkt[TCP].sport
    destination_port = pkt[TCP].dport
    tcp_data_offset = pkt[TCP].dataofs
    tcp_flags = pkt[TCP].flags
    payload_length = len(pkt[TCP].payload)

    header_information = [source_port, destination_port, ip_length, payload_length, ip_ttl, ip_tos, tcp_data_offset, int(tcp_flags)]

    return header_information


def parse_payload_bytes(pkt):
    payload_bytes = []

    payload = pkt[TCP].payload

    for byte in bytes(payload):
        payload_bytes.append(byte)

    return payload_bytes


def write_tab_to_csv(data):
    global output_csv_file
    
    with open(output_csv_file, 'a') as csvfile:
        for byte in data:
            csvfile.write(str(byte))
            csvfile.write(" ")
        csvfile.write("\n")
        csvfile.close()

def read_config_file():
    config_file = configparser.ConfigParser()
    global output_csv_file
    global input_pcap_file
    global network_interface
    global capture_pcap_mode

    current_folder = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_folder, "npfhp.conf")

    config_file.read(config_file_path)
    output_csv_file = config_file.get('CONVERT_PCAP_TO_CSV', 'OutputCSVFile')
    input_pcap_file = config_file.get('CONVERT_PCAP_TO_CSV', 'InputPCAPFile')
    network_interface = config_file.get('CONVERT_PCAP_TO_CSV', 'NetworkInterface')
    capture_pcap_mode = int(config_file.get('CONVERT_PCAP_TO_CSV', 'CapturePCAPMode'))


def sniff_network_interface():
    global network_interface
    global packets

    packets = sniff(iface=network_interface, timeout=1)


def packets_processing():
    global packets
    global output_csv_file
    data_row = []

    f = open(output_csv_file, "w")
    f.write("packet_dat\n")
    f.close()
    flow_information = parse_flow_information()

    for packet in packets:
        if IP in packet:
            if TCP in packet:
                data_row.clear()
                data_row += flow_information
                data_row.append(-1)
                data_row += parse_header_information(packet)
                data_row.append(-1)
                data_row += parse_payload_bytes(packet)

                if len(data_row) > 513:
                    data_row = data_row[:513]
                elif len(data_row) < 513:
                    while len(data_row) < 513:
                        data_row.append(-1)

                write_tab_to_csv(data_row)


if __name__ == "__main__":
    read_config_file()

    if capture_pcap_mode == 0:
        while True:
            sniff_network_interface()
            packets_processing()
    elif capture_pcap_mode == 1:
        load_pcap_file()
        packets_processing()
