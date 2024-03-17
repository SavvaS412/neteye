import socket, json, time, os, sys
from device import Device, print_devices

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001
SERVER_ADDRESS = (SERVER_HOST,SERVER_PORT)

def print_devices_terminal(data_json):
    device_dict_list = json.loads(data_json)
    device_list = [Device(**device_dict) for device_dict in device_dict_list]
    os.system('cls')
    print_devices(device_list)


def start_client(server_address):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)
    print(f"Connected to server at {server_address}")
    
    while True:
        try:
            data_json = client_socket.recv(10240).decode()
            print_devices_terminal(data_json)
            time.sleep(5)
        except Exception as e:
            print(f"ERR: {e}")
            break
    client_socket.close()

if __name__ == "__main__":
    if len(sys.argv) > 2:
        server_address = (sys.argv[1],sys.argv[2])
    elif len(sys.argv) > 1:
        server_address = (sys.argv[1],5001)
    else:
        server_address = SERVER_ADDRESS
    start_client(server_address)
