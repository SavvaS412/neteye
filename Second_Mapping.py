import ipaddress
import netifaces
import subprocess

def get_subnet_mask():
    try:
        # Get the default network interface
        default_interface = netifaces.gateways()['default'][netifaces.AF_INET][1]

        # Get the interface's IPv4 address and netmask
        if_info = netifaces.ifaddresses(default_interface)[netifaces.AF_INET][0]
        ip_address = if_info['addr']
        subnet_mask = if_info['netmask']

        return f"{ip_address}/{subnet_mask}"
    except Exception as e:
        print(f"Error getting subnet mask: {e}")
        return None

