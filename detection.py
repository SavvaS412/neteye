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
    if action == Action.LESS_EQUAL:
        statement = parameter <= amount

    elif action == Action.LESS:
        statement = parameter < amount

    elif action == Action.EQUAL:
        statement = parameter == amount

    elif action == Action.GREATER:
        statement = parameter > amount
        
    elif action == Action.GREATER_EQUAL:
        statement = parameter >= amount

    else:
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

def measure_latency(destination, num_packets=5):
    rtt_values = []

    for i in range(num_packets):
        send_time = time.time()

        # Send packet and wait for response
        response = send_ping(destination, timeout = 1)
        receive_time = time.time()

        if response:
            # Calculate round-trip time (RTT) in milliseconds
            rtt = (receive_time - send_time) * 1000
            rtt_values.append(rtt)

        time.sleep(1)

    if not rtt_values:
        return None

    avg_rtt = sum(rtt_values) / len(rtt_values)
    return avg_rtt

if __name__ == '__main__':
    detect_rules([Rule("test greater", 1, 150, 100), Rule("test wrong", 1, 15, 100), Rule("test equal", 0, 15, 15), Rule("test less", -1, 15, 100), Rule("test less wrong", -1, 15, 15), Rule("test less equal", -2, 15, 15), Rule("test error", 3, 15, 100)])