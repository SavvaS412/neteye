import scapy.all as scapy
import ipaddress
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

def get_interface_name(interface_guid):
    l = scapy.get_if_list()
    ifaces = scapy.IFACES.data
    my_iface = next((x for x in l if ifaces[x].guid == interface_guid), None)
    return ifaces[my_iface].name

def get_subnet_mask():
    try:
        default_interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
        global interface_name 
        interface_name = get_interface_name(default_interface)

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

    device_list = scan_network_arp(list())
    print_devices(device_list)


if __name__ == '__main__':
    main(debug_flag = False)
