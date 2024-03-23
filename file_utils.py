import json
import os
from datetime import datetime

from scapy.all import wrpcap

SETTINGS_FILE = "settings.json"

PACKET_CAPTURE_WINDOW = "packet_capture_window"
NOTIFICATION_UPDATE_INTERVAL = "notification_update_interval"
POPUP_NOTIFICATION_UPDATE_INTERVAL = "popup_notification_update_interval"
SCAN_INTERVAL = "scan_interval"  
SCAN_WHOLE_NETWORK_AGAIN_INTERVAL = "scan_whole_network_again_interval"


def export_capture(filename, capture):
    try:
        wrpcap(filename, capture)
    except FileNotFoundError as file_error:
        create_path(filename)
        wrpcap(filename, capture)

def save_capture(capture):
    now = datetime.now()
    filename = "logs/captures/" + now.strftime("%Y_%m_%d_%H_%M_%S") + ".pcap"
    try:
        export_capture(filename, capture)
        print("Saved capture successfully to", filename)
    except Exception as e:
        print(f"Error - Failed to save the capture to '{filename}': {e}")


def create_path(filename):
    path = filename.split('/')
    path.pop()
    path = '/'.join(path)
    try:
        os.makedirs(path)
        print(f"Directories created successfully at: {path}")
    except FileExistsError:
        print(f"Directories already exist at: {path}")

def load_settings():
    settings = {
    PACKET_CAPTURE_WINDOW:60,
    NOTIFICATION_UPDATE_INTERVAL:10,
    POPUP_NOTIFICATION_UPDATE_INTERVAL:30,
    SCAN_INTERVAL:10,
    SCAN_WHOLE_NETWORK_AGAIN_INTERVAL:60
    }
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as file:
                settings = json.load(file)
        else:
            with open(SETTINGS_FILE, "w") as file:
                file.write(json.dumps(settings))
        print(f"Saved settings successfully to {SETTINGS_FILE}")

    except Exception as e:
        print(f"Error - Failed to load setting '{SETTINGS_FILE}': {e}")

    return settings

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)

def get_setting(key):
    settings = load_settings()
    return settings.get(key)

def set_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)


def main():
    set_setting(SCAN_WHOLE_NETWORK_AGAIN_INTERVAL, 3777)
    

if __name__ == '__main__':
    main()