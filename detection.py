from scanning import Rule
from enum import Enum

class Action(Enum):
    LESS_EQUAL = -2
    LESS = -1
    EQUAL = 0
    GREATER = 1
    GREATER_EQUAL = 2

def check_statement(parameter : int, action : int, amount : int):
    if Action(action) == Action.LESS_EQUAL:
        statement = parameter <= amount

    elif Action(action) == Action.LESS:
        statement = parameter < amount

    elif Action(action) == Action.EQUAL:
        statement = parameter == amount

    elif Action(action) == Action.GREATER:
        statement = parameter > amount
        
    elif Action(action) == Action.GREATER_EQUAL:
        statement = parameter >= amount

    else:
        statement = False
        
    return statement 

def detect_rules(rules : list[Rule]):
    for rule in rules:
        try:
            statement = check_statement(rule.parameter, rule.action, rule.amount)
        except ValueError as e:
            print(f"ERR: unknown rule action in rule '{rule.name}' -", e)
            statement = False

        if statement:
            print("Notification:", rule.name)

        else:
            print("No Notification:", rule.name)

if __name__ == '__main__':
    detect_rules([Rule("test greater", 1, 150, 100), Rule("test wrong", 1, 15, 100), Rule("test equal", 0, 15, 15), Rule("test less", -1, 15, 100), Rule("test less wrong", -1, 15, 15), Rule("test less equal", -2, 15, 15), Rule("test error", 3, 15, 100)])