import datetime


class RedisDataResponse:
    __attrs__ = [
        "status_code",
        "reason",
        "elapsed",
        "value",
    ]

    def __init__(self):
        """初始化返回对象"""
        self._status_code = None
        self._reason = None
        self._elapsed = datetime.timedelta(0)
        self._value = None

    @property
    def value(self):
        return self._value

    @property
    def status_code(self):
        return self._status_code

    @property
    def reason(self):
        return self._reason

    @property
    def elapsed(self):
        return self._elapsed

    @reason.setter
    def reason(self, value):
        self._reason = value

    @status_code.setter
    def status_code(self, value):
        self._status_code = value

    @elapsed.setter
    def elapsed(self, value):
        self._elapsed = value

    @value.setter
    def value(self, value):
        self._value = value