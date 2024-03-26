import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)              #ignore scapy runtime warnings

import ipaddress
from multiprocessing.managers import ListProxy
import time

from network_utils import scapy, get_interface_name, get_subnet_mask
from device import Device, print_devices
from notification_manager import NotificationManager
from notification import Notification 

from file_utils import get_setting, SCAN_INTERVAL, SCAN_WHOLE_NETWORK_AGAIN_INTERVAL

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
                except (scapy.socket.herror, OSError) as host_error:        # print(f"Error getting hostname of {ip}: {host_error}")
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

def scan_network(device_list : list[Device] | ListProxy, subnet):
    try:
        network = ipaddress.IPv4Network(subnet, strict=False)                       # Create an IPv4Network object from the dynamic subnet
        for ip in network.hosts():                                                  # Iterate over all hosts in the subnet
            try:
                scan_ip(device_list, str(ip))
            except Exception as e:
                print(f"Warning skiping '{str(ip)}': {e}")

    except Exception as scan_error:
        print(f"Error scanning devices via ARP: {scan_error}")

    return device_list

def insert_device(device_list: list[Device] | ListProxy, device_to_insert: Device) -> list[Device] | ListProxy:
    if len(device_list) == 0:
        return [device_to_insert]

    subnet_info = get_subnet_mask()
    if subnet_info:
        subnet_mask = subnet_info.split('/')[1]
        insert_ip = ipaddress.ip_interface(f"{device_to_insert.ip}/{subnet_mask}").ip   # Convert to 'ipaddress'
        for i, device in enumerate(device_list):
            device_ip = ipaddress.ip_interface(f"{device.ip}/{subnet_mask}").ip
            if int(insert_ip) < int(device_ip):
                return device_list[:i] + [device_to_insert] + device_list[i:]
    
    return device_list + [device_to_insert]             # Insert at the end if network address is greater than all existing devices

def scan_ip(device_list : list[Device] | ListProxy, ip : str):
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
                    device_list[:] = insert_device(device_list, device)
                    #notify_change(), ip changed
                if device.mac != mac:
                    print(f"removed {device.mac} and added {mac} as {ip}")
                    device_list[:] = insert_device(device_list, Device(ip, 'Unknown Device', mac, -1,True))
                    #notify_add(), new device added
            else:
                print(f"added {mac} as {ip}")
                device_list[:] = insert_device(device_list, Device(ip, ping_response['name'], mac, ping_response['response_time_ms'],True))
                NotificationManager().notification_list.insert(0,Notification(f"Device Added {ip}","Map Update", f"added {mac} as {ip}"))

def update_name_or_latency(device: Device, device_details: dict[str, any]):
    if device.name != device_details['name']:
            device.name = device_details['name']
            print(f"changed name of {device.ip} to {device.name}")
            #notify_change(), name changed
    if device.latency != device_details['response_time_ms']:
        device.latency = device_details['response_time_ms']
    return device

def check_name_and_latency(device_list: list[Device] | ListProxy, index: int, device_details: dict[str, any]):
    device = device_list[index]
    if device.name != device_details['name'] or device.latency != device_details['response_time_ms']:
        device = update_name_or_latency(device, device_details)
        device_list[index] = device

    return device_list

def scan_update(device_list):
    try:
        for index in range(len(device_list) - 1, -1, -1):
            device_details = send_ping(device_list[index].ip, 1)
            if device_details:
                device_list = check_name_and_latency(device_list, index, device_details)
            else:
                device_details = send_ping(device_list[index].ip, 3) # check maybe sleep instead
                if device_details:
                    device_list = check_name_and_latency(device_list, index, device_details)
                else:
                    ip_to_remove = device_list[index].ip
                    device_list.remove(device_list[index])
                    print("removed", ip_to_remove)

    except Exception as e:
        print(f"Error updating scan: {e}")

    return device_list

def scan(device_list : list[Device] | ListProxy, notification_list):
    NotificationManager().initialize(notification_list)

    global interface_name 
    interface_name = get_interface_name()

    subnet = get_subnet_mask()
    if subnet:
        scan_again_time = get_setting(SCAN_INTERVAL)
        scan_network_time = get_setting(SCAN_WHOLE_NETWORK_AGAIN_INTERVAL)
        while True:
            device_list = scan_network(device_list, subnet)
            t = time.monotonic() + scan_network_time
            while True:
                device_list = scan_update(device_list)
                if time.monotonic() > t:
                    break
                time.sleep(scan_again_time)
    else:
        print("Exiting due to an error in obtaining the subnet.")

def main():
    global interface_name 
    interface_name = get_interface_name()

    subnet = get_subnet_mask()
    if subnet:
        scan_again_time = get_setting(SCAN_INTERVAL)
        scan_network_time = get_setting(SCAN_WHOLE_NETWORK_AGAIN_INTERVAL)
        device_list = list()

        print(f"Scanning devices in {subnet}:")
        while True:
            device_list = scan_network(device_list, subnet)
            print_devices(list(device_list))
            t = time.monotonic() + scan_network_time

            while True:
                device_list = scan_update(device_list)
                print_devices(list(device_list))
                print()
                if time.monotonic() > t:
                    break
                time.sleep(scan_again_time)
    else:
        print("Exiting due to an error in obtaining the subnet.")

if __name__ == '__main__':
    main()
