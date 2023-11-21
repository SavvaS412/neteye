import logging
from scapy.all import sr, IP, ICMP, socket
from ipaddress import IPv4Network
from socket import gethostbyaddr
import netifaces

# Ignore warnings
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

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

    try:
        # Iterate over all IP addresses in the subnet
        for ip in IPv4Network(subnet, strict=False).hosts():
            ip = str(ip)
            packet = IP(dst=ip) / ICMP()
            response, _ = sr(packet, timeout=0.2, verbose=0)

            for sent_packet, received_packet in response:
                if received_packet.haslayer(ICMP) and received_packet[ICMP].type == 0:
                    try:
                        device_name = gethostbyaddr(ip)[0]
                    except (socket.herror, OSError) as host_error:
                        # print(f"Error getting host information for {ip}: {host_error}")
                        device_name = "Unknown"

                    response_time_ms = int((received_packet.time - sent_packet.sent_time) * 1000)

                    device_details = {
                        'name': device_name,
                        'ip': ip,
                        'response_time_ms': response_time_ms
                    }

                    devices.append(device_details)
    except Exception as scan_error:
        print(f"Error scanning devices: {scan_error}")

    return devices

def main():
    subnet = get_subnet_mask()

    if subnet:
        print(f"Scanning devices in subnet: {subnet}")

        devices = discover_devices(subnet)

        if devices:
            print("Devices discovered:")
            for device in devices:
                print(f"Name: {device['name']}, IP: {device['ip']}, Response Time: {device['response_time_ms']} ms")
        else:
            print("No devices found.")
    else:
        print("Exiting due to an error in obtaining the subnet.")

if __name__ == "__main__":
    main()
