import json
import os
from datetime import datetime

from scapy.all import wrpcap

SETTINGS_FILE = "settings.json"

PACKET_CAPTURE_WINDOW = "packetCaptureWindow"
NOTIFICATION_UPDATE_INTERVAL = "notificationUpdateInterval"
POPUP_NOTIFICATION_UPDATE_INTERVAL = "popupNotificationUpdateInterval"
SCAN_INTERVAL = "scanInterval"
SCAN_WHOLE_NETWORK_AGAIN_INTERVAL = "scanWholeNetworkAgainInterval"

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
        PACKET_CAPTURE_WINDOW: 60,
        NOTIFICATION_UPDATE_INTERVAL: 10,
        POPUP_NOTIFICATION_UPDATE_INTERVAL: 30,
        SCAN_INTERVAL: 10,
        SCAN_WHOLE_NETWORK_AGAIN_INTERVAL: 60
    }
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as file:
                settings = json.load(file)
        else:
            with open(SETTINGS_FILE, "w") as file:
                file.write(json.dumps(settings))
        print(f"Loaded settings successfully from {SETTINGS_FILE}")
    except Exception as e:
        print(f"Error - Failed to load settings from '{SETTINGS_FILE}': {e}")

    return settings

def save_settings(updated_settings):
    current_settings = load_settings()
    current_settings.update(updated_settings)

    with open(SETTINGS_FILE, "w") as file:
        json.dump(current_settings, file, indent=4)
    print(f"Saved settings successfully to {SETTINGS_FILE}")

def get_setting(key):
    settings = load_settings()
    return settings.get(key)

def set_setting(key, value):
    settings = load_settings()
    settings[key] = value
    save_settings(settings)

def main():
    save_settings({PACKET_CAPTURE_WINDOW: 120, NOTIFICATION_UPDATE_INTERVAL: 15, POPUP_NOTIFICATION_UPDATE_INTERVAL: 45, SCAN_INTERVAL: 15, SCAN_WHOLE_NETWORK_AGAIN_INTERVAL: 120})

if __name__ == '__main__':
    main()
