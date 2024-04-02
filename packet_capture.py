from scapy.all import sniff
from scapy.layers.all import Ether, IP, TCP, UDP, ICMP, ARP, DNS, DHCP, Raw, GRE, PPP, STP, IPv6      #RawPDU, MPLS
from time import sleep
from datetime import datetime

from detection import detect_dos_attacks, detect_scanning, NetworkScan, PortScanUDP, PortScanXMAS, PortScanNULL
from network_utils import get_interface_name, get_ip
from file_utils import save_capture, get_setting, PACKET_CAPTURE_WINDOW

PACKET_LIMIT = 1000

def packet_to_json(packet):
    json_data = {"summary" : packet.summary(), "layers" : {}}
    try:
        if packet.haslayer(Ether):
            json_data["layers"]["Ethernet"] = {
                "src": str(packet[Ether].src),
                "dst": str(packet[Ether].dst),
                "type": str(packet[Ether].type),
                # Add more fields for Ethernet layer as needed
            }
        if packet.haslayer(IP):
            json_data["layers"]["IP"] = {
                "src": str(packet[IP].src),
                "dst": str(packet[IP].dst),
                "proto": str(packet[IP].proto),
                # Add more fields for IP layer as needed
            }
        if packet.haslayer(TCP):
            json_data["layers"]["TCP"] = {
                "sport": str(packet[TCP].sport),
                "dport": str(packet[TCP].dport),
                # Add more fields for TCP layer as needed
            }
        if packet.haslayer(UDP):
            json_data["layers"]["UDP"] = {
                "sport": str(packet[UDP].sport),
                "dport": str(packet[UDP].dport),
                # Add more fields for UDP layer as needed
            }
        if packet.haslayer(ICMP):
            json_data["layers"]["ICMP"] = {
                "type": str(packet[ICMP].type),
                "code": str(packet[ICMP].code),
                # Add more fields for ICMP layer as needed
            }
        if packet.haslayer(ARP):
            json_data["layers"]["ARP"] = {
                "psrc": str(packet[ARP].psrc),
                "pdst": str(packet[ARP].pdst),
                "op": str(packet[ARP].op),
                # Add more fields for ARP layer as needed
            }
        if packet.haslayer(DNS):  # DNS layer
            json_data["layers"]["DNS"] = {
                "id": str(packet[DNS].id),
                "qr": str(packet[DNS].qr),
                "qd": str(packet[DNS].qd),  # Question name (if available)
                # Add more fields for DNS layer as needed
            }
        if packet.haslayer(DHCP):  # DHCP layer
            json_data["layers"]["DHCP"] = {
                # Add more fields for DHCP layer as needed
            }
            
            if hasattr(packet[DHCP], "xid"):
                json_data["layers"]["DHCP"]["xid"] =str(packet[DHCP].xid)
            if hasattr(packet[DHCP], "op"):
                json_data["layers"]["DHCP"]["op"] = str(packet[DHCP].op)
        # Higher-level protocols (basic checks based on payload)
        if packet.haslayer(Raw):          #, RawPDU
            if hasattr(packet[Raw], "load"):
                payload = packet[Raw].load.decode("UTF-8", errors="replace")
                if payload.startswith("GET ") or payload.startswith("POST "):
                    json_data["layers"]["HTTP"] = {"type": "HTTP", "payload" : payload}  # Basic check
                elif payload.startswith("CONNECT ") and (packet.haslayer(TCP) and packet[TCP].sport == 443) or (packet.haslayer(UDP) and packet[UDP].sport == 443):  # Basic HTTPS check
                    json_data["layers"]["HTTPS"] = {"type": "HTTPS"}
                elif payload.startswith("USER ") or payload.startswith("AUTH ") or payload.startswith("PASS "):  # Basic SMTP check
                    json_data["layers"]["SMTP"] = {"type": "SMTP", "payload" : payload}
                elif payload.startswith("USER ") or payload.startswith("PASS ") or payload.startswith("CWD "):  # Basic FTP check
                    json_data["layers"]["FTP"] = {"type": "FTP", "payload" : payload}
        # Additional layer checks (examples)
        if packet.haslayer(GRE):  # GRE tunnel
            json_data["layers"]["GRE"] = {
                "proto": str(packet[GRE].proto)
            }  # Close the "GRE" dictionary
        if packet.haslayer(PPP):  # Point-to-Point Protocol
            json_data["layers"]["PPP"] = {
                "proto": str(packet[PPP].proto)
            }
        # if packet.haslayer(MPLS):  # MPLS header
        #     json_data["layers"]["MPLS"] = {
        #         "label": layer.label
        #     }
        if packet.haslayer(IPv6):  # IPv6 layer
            json_data["layers"]["IPv6"] = {
                "src": str(packet[IPv6].src),
                "dst": str(packet[IPv6].dst),
            }
            if hasattr(packet[IPv6], "next"):
                json_data["layers"]["IPv6"]["next"]= str(packet[IPv6].next)  # Next header protocol
        if packet.haslayer(STP):  # Spanning Tree Protocol
            json_data["layers"]["STP"] = {
                }
            if hasattr(packet[STP], "bridge_id"):
                json_data["layers"]["STP"]["bridge"] = str(packet[STP].bridge_id)
            if hasattr(packet[STP], "port_id"):
                json_data["layers"]["STP"]["port"] = str(packet[STP].port_id)
            if hasattr(packet[STP], "proto"):
                json_data["layers"]["STP"]["proto"] = str(packet[STP].proto)
        # Add more layer checks and extraction as needed

    except (ZeroDivisionError) as e:     #KeyError, AttributeError
        pass  # Handle potential missing fields/attributes gracefully

    return json_data

def print_packet(packet):
    print(packet.summary())

def get_statistics(capture, ip = get_ip()):
    data_received = 0
    data_sent = 0
    for packet in capture:
        if packet.haslayer(IP):
            if packet[IP].dst == ip:
                data_received += len(packet)
            else:
                data_sent += len(packet)

    return data_sent + data_received, data_received, data_sent

def check_dos_attack(packet, dos_packets_by_ip, dos_packet_count, dos_target_ip):
    if IP in packet and packet[IP].dst in dos_target_ip:
        if packet[IP].src not in dos_packets_by_ip.keys():
            dos_packets_by_ip[packet[IP].src] = 0
        dos_packets_by_ip[packet[IP].src] += 1
        dos_packet_count += 1
    return dos_packets_by_ip, dos_packet_count

def check_network_scanning(packet, network_scanning_packets_by_ip):
    if ICMP in packet and packet[ICMP].type == 8:
        if IP in packet and packet[IP].src != get_ip() and packet[IP].dst != get_ip(): 
            if packet[IP].src not in network_scanning_packets_by_ip.keys():
                network_scanning_packets_by_ip[packet[IP].src] = [packet[IP].dst]
            else:
                if packet[IP].dst not in network_scanning_packets_by_ip[packet[IP].src]:
                    network_scanning_packets_by_ip[packet[IP].src].append([packet[IP].dst])
    return network_scanning_packets_by_ip

def check_port_scanning_udp(packet, port_scanning_udp_by_ip):
    if UDP in packet and packet[UDP].len == 8 and IP in packet:
        if packet[IP].src not in port_scanning_udp_by_ip.keys():
            port_scanning_udp_by_ip[packet[IP].src] = [packet[UDP].dport]
        else:
            if packet[UDP].dport not in port_scanning_udp_by_ip[packet[IP].src]:
                port_scanning_udp_by_ip[packet[IP].src].append(packet[UDP].dport)
    return port_scanning_udp_by_ip

def check_port_scanning_xmas(packet, port_scanning_xmas_by_ip):
    if packet[TCP].flags == 0x29:
        if packet[IP].src not in port_scanning_xmas_by_ip.keys():
            port_scanning_xmas_by_ip[packet[IP].src] = [packet[TCP].dport]
        else:
            if packet[TCP].dport not in port_scanning_xmas_by_ip[packet[IP].src]:
                port_scanning_xmas_by_ip[packet[IP].src].append(packet[TCP].dport)
    return port_scanning_xmas_by_ip

def check_port_scanning_null(packet, port_scanning_null_by_ip):
    if packet[TCP].flags == 0x0:
        if packet[IP].src not in port_scanning_null_by_ip.keys():
            port_scanning_null_by_ip[packet[IP].src] = [packet[TCP].dport]
        else:
            if packet[TCP].dport not in port_scanning_null_by_ip[packet[IP].src]:
                port_scanning_null_by_ip[packet[IP].src].append(packet[TCP].dport)
    return port_scanning_null_by_ip

def capture(window_size=get_setting(PACKET_CAPTURE_WINDOW), packet_list = None):       
    global interface_name 
    interface_name = get_interface_name()        
    dos_avg_packets_per_second = 0
    first_iteration = True
    dos_target_ip = [get_ip()]
    while True:
        dos_packet_count = 0                # packets that ip.dst == me
        dos_packets_by_ip = dict()
        network_scanning_packets_by_ip = dict()
        port_scanning_udp_by_ip = dict()
        port_scanning_xmas_by_ip = dict()
        port_scanning_null_by_ip = dict()

        def packet_callback(packet):
            if packet_list is not None:
                packet_list.insert(0, packet)

            nonlocal dos_packet_count, dos_packets_by_ip, network_scanning_packets_by_ip, port_scanning_udp_by_ip, port_scanning_xmas_by_ip, port_scanning_null_by_ip

            dos_packets_by_ip, dos_packet_count = check_dos_attack(packet, dos_packets_by_ip, dos_packet_count, dos_target_ip)
            
            network_scanning_packets_by_ip = check_network_scanning(packet, network_scanning_packets_by_ip)

            port_scanning_udp_by_ip = check_port_scanning_udp(packet, port_scanning_udp_by_ip)

            if TCP in packet:
                port_scanning_xmas_by_ip = check_port_scanning_xmas(packet, port_scanning_xmas_by_ip)
                port_scanning_null_by_ip = check_port_scanning_null(packet, port_scanning_null_by_ip)

        capture = sniff(iface=interface_name, prn=packet_callback, timeout=window_size)

        save_capture(capture)

        data_total, data_received, data_sent = get_statistics(capture)

        dos_packets_per_second = dos_packet_count / window_size

        if first_iteration:
            dos_avg_packets_per_second = dos_packets_per_second

        else:
            detect_dos_attacks(dos_packets_per_second, dos_avg_packets_per_second, dos_packets_by_ip, window_size)
            detect_scanning(network_scanning_packets_by_ip, NetworkScan())
            detect_scanning(port_scanning_udp_by_ip, PortScanUDP())
            detect_scanning(port_scanning_xmas_by_ip, PortScanXMAS())
            detect_scanning(port_scanning_null_by_ip, PortScanNULL())

        first_iteration = False

        dos_avg_packets_per_second = (dos_packets_per_second + dos_avg_packets_per_second) / 2

        if packet_list is not None and len(packet_list) > PACKET_LIMIT:
            packet_list[:] = packet_list[:PACKET_LIMIT]

def main():
    capture()

if __name__ == '__main__':
    main()
