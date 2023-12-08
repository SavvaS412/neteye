from scanning import Rule
from enum import Enum

class Action(Enum):
    LESS_EQUAL = -2
    LESS = -1
    EQUAL = 0
    GREATER = 1
    GREATER_EQUAL = 2

def detect_rules(rules : list[Rule]):
    for rule in rules:
        if rule.action == 1:
            statement = rule.parameter > rule.amount
        
        else:
            print("ERR: unknown rule action", rule.name, rule.action)
            statement = False

        if statement:
            print("Notification!", rule.name)


if __name__ == '__main__':
    detect_rules([Rule("latencytest", 1, 150, 100), Rule("latencytest2", 1, 15, 100)])