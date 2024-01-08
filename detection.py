from scanning import Rule, send_ping
from enum import Enum
import time
from scapy.all import IP, ICMP, sr1

class Action(Enum):
    LESS_EQUAL = -2
    LESS = -1
    EQUAL = 0
    GREATER = 1
    GREATER_EQUAL = 2

class Parameter(Enum):
    DATA_TOTAL = 1
    DATA_RECIEVED = 2
    DATA_SENT = 3
    DATA_PER_SECOND_TOTAL = 4
    DATA_PER_SECOND_RECIEVED = 5
    DATA_PER_SECOND_SENT = 6
    PACKET_LOSS = 7
    LATENCY = 8
    #...
    
def check_statement(parameter : int, action : Action, amount : int) -> bool:
    match action:
        case Action.LESS_EQUAL:
            statement = parameter <= amount

        case Action.LESS:
            statement = parameter < amount

        case Action.EQUAL:
            statement = parameter == amount

        case Action.GREATER:
            statement = parameter > amount
        
        case Action.GREATER_EQUAL:
            statement = parameter >= amount

        case _:
            statement = False

    return statement 

def detect_rules(rules : list[Rule]):
    for rule in rules:
        try:
            statement = check_statement(rule.parameter, Action(rule.action), rule.amount)
        except ValueError as e:
            print(f"ERR: unknown rule action in rule '{rule.name}' -", e)
            statement = False

        if statement:
            print("Notification:", rule.name)

        else:
            print("No Notification:", rule.name)

def send_and_check_packets(destination, num_packets = 10):
    sent_packets = []
    received_packets = []

    for i in range(num_packets):
        response = send_ping(destination, 1)
        sent_packets.append(response)

        # Send packet and wait for response
        response = sr1(response, timeout = 1, verbose=0)

        # Check if response is received
        if response:
            received_packets.append(response)

        time.sleep(1)

    packet_loss_percentage = ((num_packets - len(received_packets)) / num_packets) * 100
    return round(packet_loss_percentage, 2)


if __name__ == '__main__':
    detect_rules([Rule("test greater", 1, 150, 100), Rule("test wrong", 1, 15, 100), Rule("test equal", 0, 15, 15), Rule("test less", -1, 15, 100), Rule("test less wrong", -1, 15, 15), Rule("test less equal", -2, 15, 15), Rule("test error", 3, 15, 100)])