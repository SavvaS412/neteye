import scapy.all as scapy
import ipaddress
from socket import gethostbyaddr, herror
import netifaces

class Device():
    def __init__(self, ip:str, name:str, mac:str, latency:int, is_available:bool):
        self.ip = ip
        self.name = name
        self.mac = mac
        self.latency = latency              #ping in ms
        self.is_available = is_available

    def is_active(self) -> bool:
        return self.is_available

    def __str__(self) -> str:
        if self.is_available:
            status = "[V]"
        else:
            status = "[X]"
        return f"{status} {self.name} - {self.ip} , {self.mac} , {self.latency}ms"

def get_interface_name():
    interface_guid = netifaces.gateways()['default'][netifaces.AF_INET][1]
    l = scapy.get_if_list()
    ifaces = scapy.IFACES.data
    my_iface = next((x for x in l if ifaces[x].guid == interface_guid), None)
    return ifaces[my_iface].name

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

def send_arp(ip):
    arp_request = scapy.ARP(pdst = ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")

    try:
        ans, unans = scapy.srp(broadcast/arp_request, iface = interface_name, timeout=0.1, verbose=debug)
        mac = ans[0][1].hwsrc
    except Exception:
        return None
    return mac


def send_ping(ip):
    packet = scapy.IP(dst=ip) / scapy.ICMP()
    try:
        response, _ = scapy.sr(packet, timeout=0.2, verbose=0)

        for sent_packet, received_packet in response:
            if received_packet.haslayer(scapy.ICMP) and received_packet[scapy.ICMP].type == 0:
                try:
                    device_name = gethostbyaddr(ip)[0]
                except (herror, OSError) as host_error:
                    print(f"Error getting hostname of {ip}: {host_error}")
                    device_name = "Unknown"

                response_time_ms = int((received_packet.time - sent_packet.sent_time) * 1000)

                device_details = {
                    'name': device_name,
                    'ip': ip,
                    'response_time_ms': response_time_ms
                }
                return device_details

    except Exception as e:
        print(f"Error sending ping requests to {ip}: {e}")
        return None

def scan_network_arp(device_list : list[Device]):
    subnet = get_subnet_mask()

    if subnet:
        network = ipaddress.IPv4Network(subnet, strict=False)                       # Create an IPv4Network object from the dynamic subnet
        for ip in network.hosts():                                                  # Iterate over all hosts in the subnet
            ip = str(ip)
            mac = send_arp(ip)
            if mac:
                if debug:
                    print("added", ip)
                device_list.append(Device(ip, 'Unknown Device', mac, -1,True))

    return device_list

def print_devices(devices : list[Device]):
    if devices:
            print("Devices discovered:")
            for device in devices:
                print(device)
    
    else:
        print("No devices found.")

def main(debug_flag):
    global debug
    debug = debug_flag

    global interface_name 
    interface_name = get_interface_name()

    device_list = scan_network_arp(list())
    print_devices(device_list)


if __name__ == '__main__':
    main(debug_flag = False)
