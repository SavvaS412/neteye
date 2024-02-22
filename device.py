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