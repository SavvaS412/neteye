import requests , json, time, os, sys
from device import Device, print_devices
from notification import Notification

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000
SERVER_ADDRESS = (SERVER_HOST,SERVER_PORT)

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


def get_choice(choices):
    choice = -1
    print("Your options are:")
    for i, choice in enumerate(choices):
        print(f"{i + 1}. {choice.__name__}")
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

def get_devices(session, base_url):
    data = session.get(base_url + "/api/map")
    return data.text

def get_last_notifications(session, base_url):
    data = session.get(base_url + "/api/notifications")
    return data.text

def print_devices_terminal(data_json):
    device_dict_list = json.loads(data_json)
    device_list = [Device(**device_dict) for device_dict in device_dict_list]
    os.system('cls')
    print_devices(device_list)

def print_last_notifications(notifications_dict_list):
    #notifications_list = [Notification(**notification_dict) for notification_dict in notifications_dict_list]
    os.system('cls')
    print("Active notifications:\t\t", time.strftime("%d.%m.%y | %H:%M:%S"))
    for notification in notifications_dict_list:
        print(f"{notification['id']}, {notification['name']}, {notification['type']}, {notification['description']}, {notification['date']}, {'read' if notification['is_read'] else 'not read'}")
  
def monitor_devices(session, base_url):
    data_json = get_devices(session, base_url)
    print_devices_terminal(data_json)

def monitor_notifications(session, base_url):
    data_json = get_last_notifications(session, base_url)
    data_dict_list = json.loads(data_json)
    data_dict_list.reverse()
    for notification_dict in data_dict_list:
        notifications_dict_list.insert(0, notification_dict)
    print_last_notifications(notifications_dict_list)

REQUESTS = [monitor_devices, lambda: print, monitor_notifications]

def start_client(server_address, request):
    session = requests.Session()
    print(f"Connected to server at {server_address}")
    base_url = f"http://{server_address[0]}:{server_address[1]}"

    client_logic_func = REQUESTS[request]

    global notifications_dict_list 
    notifications_dict_list = Notification.get_all() if request == 2 else []
    while True:
        try:
            client_logic_func(session, base_url)
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

def main():
    print_welcome_hero()
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
    print("Exiting", end='')
    time.sleep(1)
    print(".", end='')
    time.sleep(1)
    print(".", end='')
    time.sleep(1)
    print(".", end='')

if __name__ == "__main__":
    main()
