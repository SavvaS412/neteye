from scapy.all import sr1, IP, ICMP
from ipaddress import IPv4Network
import netifaces
import subprocess


def get_subnet_mask():
    try:
        # Get the default network interface
        default_interface = netifaces.gateways()['default'][netifaces.AF_INET][1]

        # Get the interface's IPv4 address and netmask
        if_info = netifaces.ifaddresses(default_interface)[netifaces.AF_INET][0]
        ip_address = if_info['addr']
        subnet_mask = if_info['netmask']

        broadcast = if_info['broadcast']

        return f"{ip_address}/{subnet_mask}", broadcast
    except Exception as e:
        print(f"Error getting subnet mask: {e}")
        return None


def discover_devices(subnet, broadcast):
    devices = []

    # Iterate over all IP addresses in the subnet

    # for ip in IPv4Network(subnet, strict=False).hosts():
    ip = str(broadcast)
    
    packet = IP(dst=ip)/ICMP()
    response = sr1(packet, timeout=1, verbose=0)

    if response and response.haslayer(ICMP) and response[ICMP].type == 0:
        print(ip)
        devices.append(ip)

    return devices

def main():
    subnet, broadcast = get_subnet_mask()

    print(f"Scanning devices in subnet: {subnet}")

    devices = discover_devices(subnet, broadcast)

    if devices:
        print("Devices discovered:")
        for device in devices:
            print(device)
    else:
        print("No devices found.")

if __name__ == "__main__":
    main()