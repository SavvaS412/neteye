from scapy.all import sr, IP, ICMP
from ipaddress import IPv4Network
import netifaces
import subprocess


def get_subnet_mask():
    try:
        # Get the default network interface
        default_interface = netifaces.gateways()['default'][netifaces.AF_INET][1]

        if_info = netifaces.ifaddresses(default_interface)[netifaces.AF_INET][0]
        ip_address = if_info['addr']
        subnet_mask = if_info['netmask']
        return f"{ip_address}/{subnet_mask}"
    
    except Exception as e:
        print(f"Error getting subnet mask: {e}")
        return None


def discover_devices(subnet):
    devices = []

    # Iterate over all IP addresses in the subnet
    for ip in IPv4Network(subnet, strict=False).hosts():
        ip = str(ip)
        packet = IP(dst=ip)/ICMP()
        response, _ = sr(packet, timeout=0.2, verbose=0)

        for sent_packet, received_packet in response:
            if received_packet.haslayer(ICMP) and received_packet[ICMP].type == 0:
                devices.append(ip)

    return devices

def main():
    subnet = get_subnet_mask()

    print(f"Scanning devices in subnet: {subnet}")

    devices = discover_devices(subnet)

    if devices:
        print("Devices discovered:")
        for device in devices:
            print(device)
    else:
        print("No devices found.")

if __name__ == "__main__":
    main()