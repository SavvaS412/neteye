from scanning import Rule
from enum import Enum

class Action(Enum):
    LESS_EQUAL = -2
    LESS = -1
    EQUAL = 0
    GREATER = 1
    GREATER_EQUAL = 2

def check_statement(parameter, action, amount):
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
        return None

    return statement 

def detect_rules(rules : list[Rule]):
    for rule in rules:
        statement = check_statement(rule.parameter, rule.action, rule.amount)

        if statement:
            print("Notification:", rule.name)

        elif not statement:
            print("No Notification:", rule.name)

        else:
            print("ERR: unknown rule action", rule.name, rule.action)


if __name__ == '__main__':
    detect_rules([Rule("latencytest", 1, 150, 100), Rule("latencytest2", 1, 15, 100)])