import scapy.all as scapy
def print_packet(packet):
    print(packet.summary())

def main():
    capture = scapy.sniff(iface="Ethernet", prn=print_packet)
    print()
    print(capture)

if __name__ == '__main__':
    main()
