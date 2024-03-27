import netifaces
import scapy.all as scapy

def get_interface_name():
    interface_guid = netifaces.gateways()['default'][netifaces.AF_INET][1]
    l = scapy.get_if_list()
    ifaces = scapy.IFACES.data
    my_iface = next((x for x in l if ifaces[x].guid == interface_guid), None)
    return ifaces[my_iface].name

def get_ip():
    try:
        if_info = netifaces.ifaddresses(netifaces.gateways()['default'][netifaces.AF_INET][1])[netifaces.AF_INET][0]            # Get the interface's IPv4 address and netmask
        ip_address = if_info['addr']

        return f"{ip_address}"
    except Exception as e:
        print(f"Error getting subnet mask: {e}")
        return None

def get_subnet_mask():
    try:
        default_interface = netifaces.gateways()['default'][netifaces.AF_INET][1]

        if_info = netifaces.ifaddresses(default_interface)[netifaces.AF_INET][0]            # Get the interface's IPv4 address and netmask
        ip_address = if_info['addr']
        subnet_mask = if_info['netmask']

        return f"{ip_address}/{subnet_mask}"
    except Exception as e:
        print(f"Error getting subnet mask: {e}")
        return None

def get_capture_packet_types(capture):
    tcp_amount = 0
    udp_amount = 0
    other_amount = 0
    
    for packet in capture:
        if scapy.TCP in packet:
            tcp_amount += 1
        elif scapy.UDP in packet:
            udp_amount += 1
        else:
            other_amount += 1
    
    return tcp_amount, udp_amount, other_amount