class NotificationManager(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(NotificationManager, cls).__new__(cls)
        return cls.instance
    
    def initialize(self, notification_list):
        self.notification_list = notification_list