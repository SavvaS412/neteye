from scanning import Rule
from enum import Enum

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
    
def calculate_dynamic_threshold(packets_per_second, threshold_factor):
    dynamic_threshold = threshold_factor * packets_per_second
    return dynamic_threshold

def update_threshold_factor(previous_packets_per_second, current_packets_per_second, threshold_factor, smoothing_factor=0.1):
    moving_average = smoothing_factor * current_packets_per_second + (1 - smoothing_factor) * previous_packets_per_second
    updated_threshold_factor = moving_average / current_packets_per_second
    return updated_threshold_factor

def detect_ddos(elapsed_time, packets_per_second, previous_packets_per_second):
    initial_threshold_factor = 2  # Initial value for threshold_factor
    initial_smoothing_factor = 0.1  # Initial value for smoothing_factor

    dynamic_threshold = calculate_dynamic_threshold(packets_per_second, initial_threshold_factor)

    print(f"Detected {packets_per_second} packets in {elapsed_time:.2f} seconds.")
    print(f"Packets per second: {packets_per_second:.2f}")
    print(f"Dynamic Threshold: {dynamic_threshold:.2f}")

    if packets_per_second > dynamic_threshold:
        print("Possible DDoS attack detected!")
        #notify_ddos()

    threshold_factor = update_threshold_factor(previous_packets_per_second, packets_per_second, initial_threshold_factor, initial_smoothing_factor)
    print(f"Updated Threshold Factor: {threshold_factor:.2f}")

    return dynamic_threshold, threshold_factor

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

if __name__ == '__main__':
    detect_rules([Rule("test greater", 1, 150, 100), Rule("test wrong", 1, 15, 100), Rule("test equal", 0, 15, 15), Rule("test less", -1, 15, 100), Rule("test less wrong", -1, 15, 15), Rule("test less equal", -2, 15, 15), Rule("test error", 3, 15, 100)])