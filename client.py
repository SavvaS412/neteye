import socket, json, time, os, sys
from device import Device, print_devices
from notification import Notification
from app_no_gui import REQUESTS

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5001
SERVER_ADDRESS = (SERVER_HOST,SERVER_PORT)

def get_choice(choices):
    choice = -1
    while True:
        choice = input("Enter Your Desired Action: ")
        try:
            choice = int(choice) - 1 
            if choice in range(len(choices)):
                return choice
            else:
                print(f"Choice must be between 1 and {len(choices)}")
        except ValueError:
            print(f"ERR: Invalid Input. Choose a number between 1 and {len(choices)}")
        except Exception as e:
            print(f"ERR at get_choice: {e}")

def print_devices_terminal(data_json):
    device_dict_list = json.loads(data_json)
    device_list = [Device(**device_dict) for device_dict in device_dict_list]
    os.system('cls')
    print_devices(device_list)

def print_last_notifications(data_json):
    notifications_dict_list = json.loads(data_json)
    #notifications_list = [Notification(**notification_dict) for notification_dict in notifications_dict_list]
    os.system('cls')
    print("Active Notifications:\t\t", time.strftime("%d.%m.%y | %H:%M:%S"))
    for n in notifications_dict_list:
        print(n["id"], n["name"], n["type"])

REQUESTS_CALLBACK = [print_devices_terminal, lambda: print, print_last_notifications]

def start_client(server_address, request = 0):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)
    print(f"Connected to server at {server_address}")
    
    while True:
        try:
            client_socket.sendall(REQUESTS[request].encode())
            data_json = client_socket.recv(10240).decode()
            REQUESTS_CALLBACK[request](data_json)
            time.sleep(5)                                   #TODO to take out of settings json
        except KeyboardInterrupt:
            break
        except json.decoder.JSONDecodeError as e:
            print(f"ERR: JSON Decoder - {e}")
            print("Skipping current frame...")
        except Exception as e:
            print(f"ERR: {e}")
            time.sleep(1)
            break
    print("Closing socket...")
    client_socket.close()
    print("Socket successfully closed")

def main():
    if len(sys.argv) > 3:
        try:
            request = int(sys.argv[3])
        except Exception:
            request = get_choice(REQUESTS)
    else:
        request = get_choice(REQUESTS)

    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            port = SERVER_PORT
        server_address = (sys.argv[1],port)
    elif len(sys.argv) > 1:
        server_address = (sys.argv[1],SERVER_PORT)
    else:
        server_address = SERVER_ADDRESS
    start_client(server_address, request)
    time.sleep(3)

if __name__ == "__main__":
    main()
