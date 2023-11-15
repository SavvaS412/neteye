from scapy.all import *

class Device():
    def __init__(self, ip:str, name:str, mac:str, is_available:bool):
        self.ip = ip
        self.name = name
        self.mac = mac
        self.is_available = is_available

    def is_active(self) -> bool:
        return self.is_available



def scan_arp(device_list : list[Device]):
    pass

def main():
    pass


if __name__ == '__main__':
    main()
