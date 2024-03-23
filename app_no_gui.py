import os, subprocess
import socket, json, time
from multiprocessing import Manager, Process
import threading
import datetime

from scanning import scan

SERVER_ADDRESS = ("127.0.0.1",5001)

REQUESTS = ["1", "2", "3"]

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

def update_map(client_socket, device_list):
    device_dicts = [device.__dict__ for device in list(device_list)]
    data_json = json.dumps(device_dicts).encode()
    client_socket.sendall(data_json)

def update_notifications_cache_list(notification_list ,notification_cache_list):
    for notification in notification_list:
        if notification not in notification_cache_list:
            print(notification)
            notification_cache_list.append(notification)

    for notification in notification_cache_list:
        if notification not in notification_list:
            notification_cache_list.remove(notification)
    return notification_cache_list 
    
def update_notifications(client_socket, notification_cache_list):
    notification_dicts = [notification.__dict__ for notification in list(notification_cache_list)]
    for notification in notification_dicts:
        notification["date"] = str(notification["date"])
    data_json = json.dumps(notification_dicts).encode()
    client_socket.sendall(data_json)


def handle_client(client_socket, client_address, device_list, notification_list):
    notification_cache_list = []
    print(f"Accepted connection from {client_address}")
    try:
        while True:
            choice = client_socket.recv(16).decode()
            if not choice:
                print(f"Disconnected from {client_address}")
                break
            if choice == REQUESTS[0]:
                update_map(client_socket, device_list)
            if choice == REQUESTS[2]:
                notification_cache_list = update_notifications_cache_list(notification_list, notification_cache_list)
                print("handle_client after",len(notification_list), len(notification_cache_list))
                update_notifications(client_socket, notification_cache_list)
            
            time.sleep(1)
    except Exception as e:
        print(f"ERR: Connection from {client_address} closed - {e}")
        try:
            client_socket.close()
        except:
            pass

def start_server(address, device_list, notification_list):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(address)
    server_socket.listen(5)
    print(f"Server listening on {address}")
    
    while True:
        client_socket, client_address = server_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address, device_list, notification_list,))
        client_handler.start()

def delete_old_notifications(notification_list):
    while True:
        now = datetime.datetime.now()
        for notification in notification_list:
            if now > notification.date + datetime.timedelta(minutes=3):            # to take this out of settings
                notification_list.remove(notification)
                print("delete_old_notifications remove",notification.name)
        time.sleep(10)

def main():
    manager = Manager()
    device_list = manager.list()
    notification_list = manager.list()      #todo
    
    Process(target=delete_old_notifications, args=(notification_list,), daemon=True).start()

    Process(target=scan, args=(device_list, notification_list,), daemon=True).start()

    Process(target=start_server, args=(SERVER_ADDRESS, device_list, notification_list,), daemon=True).start()

    subprocess.Popen(["start","cmd","/C","python", "client.py", SERVER_ADDRESS[0], str(SERVER_ADDRESS[1]), "0"], shell=True)      #use /K for debugging (K-keep, C-close)

    while True:
        input()

if __name__ == "__main__":
    os.system('cls')
    print_welcome_hero()
    main()