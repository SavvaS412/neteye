import scapy.all as scapy

INTERFACE = "Ethernet"

class Device():
    def __init__(self, ip:str, name:str, mac:str, is_available:bool):
        self.ip = ip
        self.name = name
        self.mac = mac
        self.is_available = is_available

    def is_active(self) -> bool:
        return self.is_available


def send_arp(ip):
    arp_request = scapy.ARP(pdst = ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")

    try:
        ans, unans = scapy.srp(broadcast/arp_request, iface = INTERFACE, timeout=0.1, verbose=False)
        mac = ans[0][1].hwsrc
    except Exception:
        return None
    return mac

def scan_network_arp(device_list : list[Device] = []):
    for i in range(1,255):
        ip = "192.168.1." + str(i)
        mac = send_arp(ip)
        if mac is not None:
            print("added", ip)
            device_list.append(Device(ip, '-', mac, True))

    return device_list


def main():
    device_list = scan_network_arp()
    print(device_list)


if __name__ == '__main__':
    main()
