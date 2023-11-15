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

def ping_subnet_dynamic():
    # Get the dynamic subnet mask
    subnet = get_subnet_mask()

    if subnet:
        # Create an IPv4Network object from the dynamic subnet
        network = ipaddress.IPv4Network(subnet, strict=False)

        # Iterate over all hosts in the subnet
        for ip in network.hosts():
            ip_str = str(ip)
            try:
                # Use the subprocess module to send a ping request
                subprocess.run(['ping', '-n', '1', ip_str], check=True)
                print(f"Ping to {ip_str} successful!")
            except subprocess.CalledProcessError:
                print(f"Ping to {ip_str} failed.")

# Example usage: Ping all hosts in the dynamically determined subnet
ping_subnet_dynamic()
