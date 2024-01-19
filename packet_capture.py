import os
import scapy.all as scapy
import netifaces
from time import monotonic_ns, sleep
from datetime import datetime
from detection import detect_dos_attacks, detect_port_scan_udp, detect_port_scan_xmas

def get_interface_name(interface_guid):
    l = scapy.get_if_list()
    ifaces = scapy.IFACES.data
    my_iface = next((x for x in l if ifaces[x].guid == interface_guid), None)
    return ifaces[my_iface].name

def get_ip():
    try:
        default_interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
        global interface_name 
        interface_name = get_interface_name(default_interface)

        if_info = netifaces.ifaddresses(default_interface)[netifaces.AF_INET][0]            # Get the interface's IPv4 address and netmask
        ip_address = if_info['addr']

        return f"{ip_address}"
    except Exception as e:
        print(f"Error getting subnet mask: {e}")
        return None

def print_packet(packet):
    print(packet.summary())

def get_statistics(capture, ip):
    data_received = 0
    data_sent = 0
    for packet in capture:
        if packet.haslayer(scapy.IP):
            if packet[scapy.IP].dst == ip:
                data_received += len(packet)
            else:
                data_sent += len(packet)

    return data_sent + data_received, data_received, data_sent

def export_capture(filename, capture):
    try:
        scapy.wrpcap(filename, capture)
    except FileNotFoundError as file_error:
        create_path(filename)
        scapy.wrpcap(filename, capture)

def create_path(filename):
    path = filename.split('/')
    path.pop()
    path = '/'.join(path)
    try:
        os.makedirs(path)
        print(f"Directories created successfully at: {path}")
    except FileExistsError:
        print(f"Directories already exist at: {path}")

def capture(window_size=30):               
    avg_packets_per_second = 0
    first_iteration = True
    ip = get_ip()
    while True:
        packet_count = 0                # packets that ip.dst == me
        packets_by_ip = dict()
        port_scanning_udp_by_ip = dict()
        port_scanning_xmas_by_ip = dict()

        t_start = monotonic_ns()

        def packet_callback(packet):
            nonlocal packet_count, packets_by_ip, port_scanning_udp_by_ip, port_scanning_xmas_by_ip

            if scapy.IP in packet and packet[scapy.IP].dst == ip:
                if packet[scapy.IP].src not in packets_by_ip.keys():
                   packets_by_ip[packet[scapy.IP].src] = 0
                packets_by_ip[packet[scapy.IP].src] += 1
                packet_count += 1

            if scapy.UDP in packet and packet[scapy.UDP].len == 8 and scapy.IP in packet:
                if packet[scapy.IP].src not in port_scanning_udp_by_ip.keys():
                   port_scanning_udp_by_ip[packet[scapy.IP].src] = [packet[scapy.UDP].dport]
                else:
                    if packet[scapy.UDP].dport not in port_scanning_udp_by_ip[packet[scapy.IP].src]:
                        port_scanning_udp_by_ip[packet[scapy.IP].src].append(packet[scapy.UDP].dport)

            if scapy.TCP in packet and packet[scapy.TCP].flags == 0x29:
                if packet[scapy.IP].src not in port_scanning_xmas_by_ip.keys():
                   port_scanning_xmas_by_ip[packet[scapy.IP].src] = [packet[scapy.TCP].dport]
                else:
                    if packet[scapy.TCP].dport not in port_scanning_xmas_by_ip[packet[scapy.IP].src]:
                        port_scanning_xmas_by_ip[packet[scapy.IP].src].append(packet[scapy.TCP].dport)

        capture = scapy.sniff(iface=interface_name, prn=packet_callback, timeout=window_size)
        t_stop = monotonic_ns()
        print()
        print(capture)
        print()

        now = datetime.now()
        filename = "logs/captures/" + now.strftime("%Y_%m_%d_%H_%M_%S") + ".pcap"
        try:
            export_capture(filename, capture)
            print("Saved capture successfully to", filename)
        except Exception as e:
            print(f"Error - Failed to save the capture to '{filename}': {e}")
        print()

        data_total, data_received, data_sent = get_statistics(capture, ip)
        print("Data Total:" + str(int(data_total/1000)) + "kb")
        print("Data Recieved:" + str(int(data_received/1000)) + "kb")
        print("Data Sent:" + str(int(data_sent/1000)) + "kb")
        print()
        
        elapsed_time = (t_stop - t_start) * 10**-9 #in seconds

        packets_per_second = packet_count / elapsed_time

        if first_iteration:
            avg_packets_per_second = packets_per_second

        else:
            detect_dos_attacks(packets_per_second, avg_packets_per_second, packets_by_ip, window_size)
            detect_port_scan_udp(port_scanning_udp_by_ip)
            detect_port_scan_xmas(port_scanning_xmas_by_ip)

        first_iteration = False

        avg_packets_per_second = (packets_per_second + avg_packets_per_second) / 2

        sleep(window_size)

def main():
    capture()

if __name__ == '__main__':
    main()
