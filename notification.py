from datetime import datetime, timedelta
import time

from db_manager import insert_notification, get_notifications

class Notification():
    def __init__(self, name:str, type:str, description:str, id:int | None = None, date:datetime = datetime(1971, 1, 1), is_read:bool =False) -> None:
        self.name = name
        self.type = type
        self.description = description
        self.is_read = is_read
            
        if date == datetime(1971, 1, 1):
            self.date = datetime.now()
        else:
            self.date = date

        self.id = id
        if id == None:
            db_id = insert_notification(self.name, self.type, self.description, self.date, self.is_read)
            if db_id:
                self.id = db_id[0]

    def __eq__(self, other):
        if isinstance(other, Notification):
            return self.id == other.id and self.name == other.name and self.type == other.type and self.description == other.description and self.date == other.date
        else:
            return False

    @classmethod
    def get_all(cls):
        notifications = []
        list_rows = get_notifications()
        
        if list_rows:
            for rows in list_rows:
                notification = Notification(name=rows[1],type=rows[2],description=rows[3],id=rows[0], date=rows[4], is_read=rows[5])
                notifications.append(notification)

        return notifications 


def delete_old_notifications(notification_list):
    while True:
        now = datetime.now()
        for notification in notification_list:
            if now > notification.date + timedelta(minutes=3):            # to take this out of settings
                notification_list.remove(notification)
                print("delete_old_notifications remove",notification.name)
        time.sleep(10)
