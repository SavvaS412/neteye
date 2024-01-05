import os
import scapy.all as scapy
import netifaces
from time import monotonic_ns, sleep
from datetime import datetime
from detection import detect_ddos

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

def capture(window_size=60):
    packet_count = 0                    # packets that ip.dst == me
    previous_packets_per_second = 0
    first_iteration = True
    ip = get_ip()
    threshold_factor = 2                # initial value for threshold factor
    while True:
        t_start = monotonic_ns()

        def packet_callback(packet):
            nonlocal packet_count

            if scapy.IP in packet and packet[scapy.IP].dst == ip:
                packet_count += 1

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

        if not first_iteration:
            threshold_factor = detect_ddos(packets_per_second, previous_packets_per_second, threshold_factor)

        packet_count = 0                #reset counters for the next window
        first_iteration = False

        previous_packets_per_second = packets_per_second

        sleep(window_size)

def main():
    capture()

if __name__ == '__main__':
    main()
