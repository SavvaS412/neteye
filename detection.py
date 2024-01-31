from scanning import Rule, send_ping
from enum import Enum
import time
from scapy.all import IP, ICMP, sr1, rdpcap

MINIMAL_PPS_RANGE = 10
LOW_PPS_RANGE = 25
MEDIUM_LOW_PPS_RANGE = 50
MEDIUM_HIGH_PPS_RANGE = 100
HIGH_PPS_RANGE = 500
ULTRA_PPS_RANGE = 1000
MAXIMUM_PPS_RANGE = 5000

NETWORK_SCAN_THRESHOLD = 10
PORT_SCAN_UDP_THRESHOLD = 10
PORT_SCAN_XMAS_THRESHOLD = 10
PORT_SCAN_NULL_THRESHOLD = 10

class Action(Enum):
    LESS_EQUAL = -2
    LESS = -1
    EQUAL = 0
    GREATER = 1
    GREATER_EQUAL = 2

class Parameter(Enum):
    DATA_TOTAL = 1
    DATA_RECIEVED = 2
    DATA_SENT = 3
    DATA_PER_SECOND_TOTAL = 4
    DATA_PER_SECOND_RECIEVED = 5
    DATA_PER_SECOND_SENT = 6
    PACKET_LOSS = 7
    LATENCY = 8
    DOS = 9
    DDOS = 10
    PORT_SCANNING = 11
    NETWORK_SCANNING = 12

class Scan:
    THRESHOLD = [10,10,10,10]

    class Type(Enum):
        NETWORK_SCAN = 0
        PORT_SCAN_UDP = 1
        PORT_SCAN_XMAS = 2
        PORT_SCAN_NULL = 3

def calculate_dynamic_dos_threshold(avg_packets_per_second : float) -> float:
    if avg_packets_per_second <= MINIMAL_PPS_RANGE:
        threshold_factor = 100
    elif avg_packets_per_second <= LOW_PPS_RANGE:
        threshold_factor = 90
    elif avg_packets_per_second <= MEDIUM_LOW_PPS_RANGE:
        threshold_factor = 75
    elif avg_packets_per_second <= MEDIUM_HIGH_PPS_RANGE:
        threshold_factor = 55
    elif avg_packets_per_second <= HIGH_PPS_RANGE:
        threshold_factor = 35
    elif avg_packets_per_second <= ULTRA_PPS_RANGE:
        threshold_factor = 10
    elif avg_packets_per_second <= MAXIMUM_PPS_RANGE:
        threshold_factor = 5
    else:
        threshold_factor = 3

    dynamic_threshold = threshold_factor * avg_packets_per_second
    return dynamic_threshold

def detect_dos( ip_dict : dict[str, int], dynamic_threshold : float, window : int):
    for potential_ip in ip_dict:
        packets_per_second = ip_dict[potential_ip] / window
        if packets_per_second > (dynamic_threshold * 0.75):
            print(f"Possible DoS attack from {potential_ip} detected!")
            #notify_dos()

def detect_ddos(packets_per_second : float, dynamic_threshold : float):
    if packets_per_second > dynamic_threshold:
        print("Possible DDoS attack detected!")
        #notify_ddos()

def detect_dos_attacks(packets_per_second : float, avg_packets_per_second : float, ip_dict : dict[str, int], window : int):
    dynamic_threshold = calculate_dynamic_dos_threshold(avg_packets_per_second)

    print(f"Packets per second: {packets_per_second:.2f}")
    print(f"Dynamic Threshold: {dynamic_threshold:.2f}")

    if True: #if there's a rule for 
        detect_dos(ip_dict, dynamic_threshold, window)
    if True:
        detect_ddos(packets_per_second, dynamic_threshold)

def detect_icmp_network_scanning(ip_dict : dict[str, list[str]]):
    for potential_ip in ip_dict:
        if len(ip_dict[potential_ip]) > NETWORK_SCAN_THRESHOLD:                    #TODO: instead of 10 use a threshold
            print(f"Possible ICMP network scan from {potential_ip} detected!")
            #notify_network_scanning()

def detect_port_scan_udp(ip_dict : dict[str, list[int]]):
    for potential_ip in ip_dict:
        if len(ip_dict[potential_ip]) > PORT_SCAN_UDP_THRESHOLD:
            print(f"Possible UDP port-scanning attack from {potential_ip} detected!")
            #notify_port_scanning()

def detect_port_scan_xmas(ip_dict : dict[str, list[int]]):
    for potential_ip in ip_dict:
        if len(ip_dict[potential_ip]) > PORT_SCAN_XMAS_THRESHOLD:
            print(f"Possible XMAS port-scanning attack from {potential_ip} detected!")
            #notify_port_scanning()

def detect_port_scan_null(ip_dict : dict[str, list[int]]):
    for potential_ip in ip_dict:
        if len(ip_dict[potential_ip]) > PORT_SCAN_NULL_THRESHOLD:
            print(f"Possible NULL port-scanning attack from {potential_ip} detected!")
            #notify_port_scanning()

def check_statement(parameter : int, action : Action, amount : int) -> bool:
    if action == Action.LESS_EQUAL:
        statement = parameter <= amount

    elif action == Action.LESS:
        statement = parameter < amount

    elif action == Action.EQUAL:
        statement = parameter == amount

    elif action == Action.GREATER:
        statement = parameter > amount
        
    elif action == Action.GREATER_EQUAL:
        statement = parameter >= amount

    else:
        statement = False

    return statement 

def detect_rules(rules : list[Rule]):
    for rule in rules:
        try:
            statement = check_statement(rule.parameter, Action(rule.action), rule.amount)
        except ValueError as e:
            print(f"ERR: unknown rule action in rule '{rule.name}' -", e)
            statement = False

        if statement:
            print("Notification:", rule.name)

        else:
            print("No Notification:", rule.name)

def measure_packet_loss(destination, num_packets = 10):
    received_packets = []

    for i in range(num_packets):
        # Send packet and wait for response
        response = send_ping(destination, timeout = 1)

        # Check if response is received
        if response:
            received_packets.append(response)

        time.sleep(1)

    packet_loss_percentage = ((num_packets - len(received_packets)) / num_packets) * 100
    return round(packet_loss_percentage, 2)

def measure_latency(destination, num_packets=5):
    rtt_values = []

    for i in range(num_packets):
        send_time = time.time()

        # Send packet and wait for response
        response = send_ping(destination, timeout = 1)
        receive_time = time.time()
        
        if response:
            # Calculate round-trip time (RTT) in milliseconds
            rtt = (receive_time - send_time) * 1000
            rtt_values.append(rtt)
        
        time.sleep(1)

        if not rtt_values:
            return None

        avg_rtt = sum(rtt_values) / len(rtt_values)
        return avg_rtt


if __name__ == '__main__':
    detect_rules([Rule("test greater", 1, 150, 100, "192.168.1.1"), Rule("test wrong", 1, 15, 100, "192.168.1.1"), Rule("test equal", 0, 15, 15, "192.168.1.1"), Rule("test less", -1, 15, 100, "192.168.1.1"), Rule("test less wrong", -1, 15, 15, "192.168.1.1"), Rule("test less equal", -2, 15, 15, "192.168.1.1"), Rule("test error", 3, 15, 100, "192.168.1.1")])