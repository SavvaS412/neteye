import scapy.all as scapy
import netifaces

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

def main():
    ip = get_ip()
    capture = scapy.sniff(iface="Ethernet", prn=print_packet)
    print()
    print(capture)
    print()

    data_total, data_received, data_sent = get_statistics(capture, ip)
    print("Data Total:" + str(int(data_total/1000)) + "kb")
    print("Data Recieved:" + str(int(data_received/1000)) + "kb")
    print("Data Sent:" + str(int(data_sent/1000)) + "kb")

if __name__ == '__main__':
    main()
