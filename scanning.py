import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)              #ignore scapy runtime warnings
import db_manager

import scapy.all as scapy
import ipaddress
import netifaces
from datetime import datetime
import time

RULE_TABLE_NAME = 'table_name'
RULE_COL_NAME = 'name'
RULE_COL_ACTION = 'action'
RULE_COL_STATEMENT = 'statement'
RULE_COL_PARAMETER = 'parameter'

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

class Rule():
    def __init__(self, name:str, action:int, parameter:int, amount:int, target:str) -> None:
        self.name = name
        self.action = action
        self.parameter = parameter
        self.amount = amount
        self.target = target

    def add_to_db(self):
        db_manager.insert_rule(self.name, self.action, self.parameter, self.amount, self.target)

class Notification():
    def __init__(self, name:str, type:str, description:str) -> None:
        self.name = name
        self.type = type
        self.description = description
        self.date = datetime.now()
        self.isRead = False
    
    def add_to_db(self):
        db_manager.insert_notification(self.name, self.type, self.description, self.date, self.isRead)

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
        ans, unans = scapy.srp(broadcast/arp_request, iface = interface_name, timeout=0.1, verbose=False)
        mac = ans[0][1].hwsrc
    except Exception as scan_error:
        return None
    return mac


def send_ping(ip, timeout):
    packet = scapy.IP(dst=ip) / scapy.ICMP()
    try:
        response, _ = scapy.sr(packet, timeout=timeout, verbose=False)

        for sent_packet, received_packet in response:
            if received_packet.haslayer(scapy.ICMP) and received_packet[scapy.ICMP].type == 0:
                try:
                    device_name = scapy.socket.gethostbyaddr(ip)[0]
                except (scapy.socket.herror, OSError) as host_error:
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

def scan_network(device_list : list[Device], subnet):
    try:
        network = ipaddress.IPv4Network(subnet, strict=False)                       # Create an IPv4Network object from the dynamic subnet
        for ip in network.hosts():                                                  # Iterate over all hosts in the subnet
            scan_ip(device_list, str(ip))

    except Exception as scan_error:
        print(f"Error scanning devices via ARP: {scan_error}")

    return device_list

def scan_ip(device_list : list[Device], ip : str):
    mac = send_arp(ip)
    if mac:
        ping_response = send_ping(ip, 1)
        device = next((device for device in device_list if device.ip == ip or device.mac == mac), None)
        if ping_response:
            if device:
                if device.ip == ip and device.mac == mac:
                    return
                device_list.remove(device)
                if device.ip != ip:
                    device.ip = ip
                    print(f"changed '{device.mac}' ip to: {ip}")
                    device_list.append(device)
                    #notify_change(), ip changed
                if device.mac != mac:
                    print(f"removed {device.mac} and added {mac} as {ip}")
                    device_list.append(Device(ip, 'Unknown Device', mac, -1,True))
                    #notify_add(), new device added
            else:
                print(f"added {mac} as {ip}")
                device_list.append(Device(ip, ping_response['name'], mac, ping_response['response_time_ms'],True))

def check_name_and_latency(device_list: list[Device], device: Device, device_details: dict[str, any]):
    if device.name != device_details['name'] or device.latency != device_details['response_time_ms']:
        device_list.remove(device)
        if device.name != device_details['name']:
            device.name = device_details['name']
            print(f"changed name of {device.ip} to {device.name}")
            #notify_change(), name changed
        if device.latency != device_details['response_time_ms']:
            device.latency = device_details['response_time_ms']
        device_list.append(device)
    return device_list

def scan_update(device_list):
    try:
        for device in device_list:
            device_details = send_ping(device.ip, 1)
            if device_details:
                device_list = check_name_and_latency(device_list, device, device_details)
            else:
                device_details = send_ping(device.ip, 3) # check maybe sleep instead
                if device_details:
                    device_list = check_name_and_latency(device_list, device, device_details)
                else:
                    device_list.remove(device)
                    print("removed", device.ip)

    except Exception as e:
        print(f"Error updating scan: {e}")

    return device_list

def print_devices(devices : list[Device]):
    if devices:
        print("Devices discovered:")
        for device in devices:
            print(device)
    
    else:
        print("No devices found.")

def main():
    global interface_name 
    interface_name = get_interface_name()

    subnet = get_subnet_mask()
    if subnet:
        scan_again_time = 30                            # In seconds
        scan_network_time = 300                         # In seconds
        device_list = list()

        print(f"Scanning devices in {subnet}:")
        while True:
            device_list = scan_network(device_list, subnet)
            print_devices(device_list)
            t = time.monotonic() + scan_network_time

            while True:
                device_list = scan_update(device_list)
                print_devices(device_list)
                print()
                if time.monotonic() > t:
                    break
                time.sleep(scan_again_time)
    else:
        print("Exiting due to an error in obtaining the subnet.")

if __name__ == '__main__':
    main()
