from db_manager import insert_notification, get_notifications

class Rule():
    def __init__(self, name:str, action:int, parameter:int, amount:int, target:str) -> None:
        self.name = name
        self.action = action
        self.parameter = parameter
        self.amount = amount
        self.target = target

    def add_to_db(self):
        db_manager.insert_rule(self.name, self.action, self.parameter, self.amount, self.target)