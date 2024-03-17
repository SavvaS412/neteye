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
    
def print_devices(devices : list[Device]):
    if devices:
        print("Devices discovered:")
        for device in devices:
            print(device)
    else:
        print("No devices found.")

def print_devices_terminal():
    import socket, json, time, os
    device_list =[]
    address = ('localhost', 5001)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect(address)
            print(f"Successfully connected to {address}")
        except ConnectionError:
            print(f"Failed to connect to {address}")
        while True:
            try:
                data_json = sock.recv(10240).decode()
                device_dict_list = json.loads(data_json)
                device_list = [Device(**device_dict) for device_dict in device_dict_list]
                os.system('cls')
                print("Devices discovered:\t\t", time.strftime("%d.%m.%y | %H:%M:%S"))
                for device in device_list:
                    print(device)
            except Exception as e:
                print("Error:", e)

            time.sleep(5)

if __name__ == '__main__':
    print_devices_terminal()