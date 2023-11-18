from scapy.all import sr, IP, UDP, DNSQR, DNS, ICMP, RandShort
from ipaddress import IPv4Network
import netifaces

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

def get_host_name(ip):
    try:
        dns_query = IP(dst='192.168.1.1') / UDP(sport=RandShort(), dport=53) / DNS(rd=1, qd=DNSQR(qname=ip, qtype='PTR'))
        response = sr(dns_query, timeout=1, verbose=0)

        print('\n',response[0][0][1],'\n')

        if response and response[0] and response[0][0] and response[0][0][DNS].an:
            host_name = response[0][0][DNS].an.rname.decode('utf-8')
            return host_name
        else:
            return None

    except Exception as e:
        print(f"Error getting hostname for {ip}: {e}")
        return None


def discover_devices(subnet):
    devices = []

    # Iterate over all IP addresses in the subnet
    for ip in IPv4Network(subnet, strict=False).hosts():
        ip = str(ip)
        packet = IP(dst=ip) / ICMP()
        response, _ = sr(packet, timeout=0.2, verbose=0)

        for sent_packet, received_packet in response:
            if received_packet.haslayer(ICMP) and received_packet[ICMP].type == 0:
                device_details = {
                    'name': get_host_name(ip) if get_host_name(ip) is not None else "Unknown",
                    'ip': ip,
                    'response_time_ms': int((received_packet.time - sent_packet.sent_time) * 1000)
                }
                devices.append(device_details)

    return devices


def main():
    subnet = get_subnet_mask()

    print(f"Scanning devices in subnet: {subnet}")

    devices = discover_devices(subnet)

    if devices:
        print("Devices discovered:")
        for device in devices:
            print(f"Name: {device['name']}, IP: {device['ip']}, Response Time: {device['response_time_ms']} ms")
    else:
        print("No devices found.")


if __name__ == "__main__":
    main()