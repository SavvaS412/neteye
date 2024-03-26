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

DEFAULT = {
    PACKET_CAPTURE_WINDOW : 30,
    NOTIFICATION_UPDATE_INTERVAL : 5,
    POPUP_NOTIFICATION_UPDATE_INTERVAL : 10,
    SCAN_INTERVAL : 5,
    SCAN_WHOLE_NETWORK_AGAIN_INTERVAL : 60
}

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
        PACKET_CAPTURE_WINDOW: {"options": [(3, "3 seconds"), (5, "5 seconds"), (10, "10 seconds"), (15, "15 seconds"), (30, "30 seconds"), (60, "1 minute"), (300, "5 minutes")]},
        NOTIFICATION_UPDATE_INTERVAL: {"options": [(3, "3 seconds"), (5, "5 seconds"), (10, "10 seconds"), (15, "15 seconds"), (30, "30 seconds"), (60, "1 minute"), (300, "5 minutes")]},
        POPUP_NOTIFICATION_UPDATE_INTERVAL: {"options": [(10, "10 seconds"), (15, "15 seconds"), (30, "30 seconds"), (60, "1 minute"), (300, "5 minutes")]},
        SCAN_INTERVAL: {"options": [(5, "5 seconds"), (10, "10 seconds"), (15, "15 seconds"), (30, "30 seconds"), (60, "1 minute"), (120, "2 minutes"), (180, "3 minutes"), (300, "5 minutes"), (600, "10 minutes")]},
        SCAN_WHOLE_NETWORK_AGAIN_INTERVAL: {"options": [(15, "15 seconds"), (30, "30 seconds"), (60, "1 minute"), (120, "2 minutes"), (180, "3 minutes"), (300, "5 minutes"), (600, "10 minutes"), (1800, "30 minutes"), (3600, "1 hour")]},
    }
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as file:
                saved_settings = json.load(file)
                for key, value in saved_settings.items():
                    settings[key]["current"] = value
        else:
            with open(SETTINGS_FILE, "w") as file:
                json.dump({key: DEFAULT[key] for key in settings.keys()}, file, indent=4)
    except Exception as e:
        print(f"Error - Failed to load settings from '{SETTINGS_FILE}': {e}")

    return settings

def save_settings(settings):
    # Save settings to a JSON file named 'settings.json'
    with open('settings.json', 'w') as file:
        json.dump(settings, file, indent=4)

def get_setting(key):
    settings = load_settings()
    setting = settings.get(key)
    if setting:
        value = setting.get("current")
        if value:
            return value
    return DEFAULT[key]

def set_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)

def main():
    save_settings({PACKET_CAPTURE_WINDOW: 120, NOTIFICATION_UPDATE_INTERVAL: 15, POPUP_NOTIFICATION_UPDATE_INTERVAL: 45, SCAN_INTERVAL: 15, SCAN_WHOLE_NETWORK_AGAIN_INTERVAL: 120})

if __name__ == '__main__':
    main()
