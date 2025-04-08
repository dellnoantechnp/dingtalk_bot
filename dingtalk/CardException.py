class PersistentDataError(Exception):
    def __init__(self, message, status):
        super().__init__(message, status)
        self.message = message
        self.status = status


class LoadPersistentDataError(Exception):
    def __init__(self, message, status):
        super().__init__(message, status)
        self.message = message
        self.status = status

class SendCardRobotNotFoundException(Exception):
    def __init__(self, origin_message, status):
        self.origin_message = origin_message
        self.message = self.origin_message + "\n" + "原因：机器人未添加至 open_conversation_id 群组中"
        super().__init__(self.message, status)
        self.status = status