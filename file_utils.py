from os import makedirs
from datetime import datetime

from scapy.all import wrpcap

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
        makedirs(path)
        print(f"Directories created successfully at: {path}")
    except FileExistsError:
        print(f"Directories already exist at: {path}")