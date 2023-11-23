import os
import scapy.all as scapy
import netifaces
from time import monotonic_ns

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

def main():
    ip = get_ip()
    t_start = monotonic_ns()
    capture = scapy.sniff(iface="Ethernet", prn=print_packet)
    t_stop = monotonic_ns()
    print()
    print(capture)
    print()

    data_total, data_received, data_sent = get_statistics(capture, ip)
    print("Data Total:" + str(int(data_total/1000)) + "kb")
    print("Data Recieved:" + str(int(data_received/1000)) + "kb")
    print("Data Sent:" + str(int(data_sent/1000)) + "kb")
    print()
    
    seconds = (t_stop - t_start) * 10**-9
    data_total_per_sec = data_total / seconds
    data_received_per_sec = data_received / seconds
    data_sent_per_sec = data_sent / seconds


    print("Data Total per Second:" + str(int(data_total_per_sec/1000)) + "kbps")
    print("Data Recieved per Second:" + str(int(data_received_per_sec/1000)) + "kbps")
    print("Data Sent per Second:" + str(int(data_sent_per_sec/1000)) + "kbps")

if __name__ == '__main__':
    main()
