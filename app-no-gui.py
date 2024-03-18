import os, subprocess, time
import socket, json
from multiprocessing import Manager, Process
import threading

from scanning import scan

SERVER_ADDRESS = ("127.0.0.1",5001)

def print_welcome_hero():
    print(
'''
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@(.           ,%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@(                               @@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@.                                         (@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@                   @@@@@@@@*                      /@@@@@@@@@@@@@@
@@@@@@@@@@@@          &        @@@@@@@@@@.                %          @@@@@@@@@@@
@@@@@@@@@         @@@&      .@@@@@.                        @@@%        .@@@@@@@@
@@@@@@#        @@@@@@      /@@@@                            @@@@@@        @@@@@@
@@@@*       @@@@@@@@*      @@@@                             @@@@@@@@(       @@@@
@@%       @@@@@@@@@@       @@@@                             @@@@@@@@@@@       @@
@       @@@@@@@@@@@@#                                       @@@@@@@@@@@@@      .
      @@@@@@@@@@@@@@@                                      ,@@@@@@@@@@@@@@/     
@      ,@@@@@@@@@@@@@@                                    .@@@@@@@@@@@@@@       
@@,      ,@@@@@@@@@@@@@.                                 #@@@@@@@@@@@@@       %@
@@@@        @@@@@@@@@@@@@                              /@@@@@@@@@@@@@       ,@@@
@@@@@@        #@@@@@@@@@@@@&                         @@@@@@@@@@@@@        (@@@@@
@@@@@@@@(        *@@@@@@@@@@@@@#                 @@@@@@@@@@@@@@         @@@@@@@@
@@@@@@@@@@@,         #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@,         %@@@@@@@@@@
@@@@@@@@@@@@@@%           (@@@@@@@@@@@@@@@@@@@@@@@@@@@,           @@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@(                ./%@@@@@#*                 &@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@#                                 &@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@(                 %@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


''')

def update_map(device_list, client_socket):
    device_dicts = [device.__dict__ for device in list(device_list)]
    data_json = json.dumps(device_dicts).encode()
    client_socket.sendall(data_json)

def handle_client(device_list, client_socket, client_address):
    print(f"Accepted connection from {client_address}")
    
    try:
        while True:
            update_map(device_list, client_socket)
            time.sleep(5)
    except Exception as e:
        print(f"ERR: Connection from {client_address} closed")
        try:
            client_socket.close()
        except:
            pass


def start_server(device_list, address):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(address)
    server_socket.listen(5)
    print(f"Server listening on {address}")
    
    while True:
        client_socket, client_address = server_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(device_list, client_socket, client_address))
        client_handler.start()

def main():
    manager = Manager()
    notification_list = manager.list()      #todo
    device_list = manager.list()
    
    Process(target=scan, args=(device_list,), daemon=True).start()

    # Start a subprocess to run print_devices.py
    Process(target=start_server, args=(device_list, SERVER_ADDRESS,), daemon=True).start()
    subprocess.Popen(["start","cmd","/C","python", "client-map-no-gui.py", SERVER_ADDRESS[0], str(SERVER_ADDRESS[1])], shell=True)      #use /K for debugging (K-keep, C-close)

    while True:
        input()

if __name__ == "__main__":
    os.system('cls')
    print_welcome_hero()
    main()