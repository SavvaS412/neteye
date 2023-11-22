import logging
from scapy.all import sr, IP, ICMP, socket
from ipaddress import IPv4Network
from socket import gethostbyaddr
import netifaces
import time

# Ignore warnings
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

def update_scan(devices):
    try:
        updated_devices = []
        for i in range(len(devices)):
            device = devices[i]
            updated_devices = send_ping_requests(device['ip'], updated_devices)

        devices = updated_devices

    except Exception as e:
        print(f"Error updating scan: {e}")

    return devices



def discover_devices(subnet):
    devices = []

    try:
        # Iterate over all IP addresses in the subnet
        for ip in IPv4Network(subnet, strict=False).hosts():
            ip = str(ip)
            devices = send_ping_requests(ip, devices)
            
    except Exception as scan_error:
        print(f"Error scanning devices: {scan_error}")

    return devices

def main():
    subnet = get_subnet_mask()

    if subnet:
        print(f"Scanning devices in subnet: {subnet}")
        devices = discover_devices(subnet)
        print_devices(devices)

        scan_again_time = 30 # In seconds
        while True:
            time.sleep(scan_again_time)
            
            print(f"\nScanning devices again in subnet: {subnet}")
            devices = update_scan(devices)
            print_devices(devices)

    else:
        print("Exiting due to an error in obtaining the subnet.")

if __name__ == "__main__":
    main()
