import datetime


class RedisDataResponse:
    __attrs__ = [
        "status_code",
        "reason",
        "elapsed",
        "value",
        "raw_value",
        "ok"
    ]

    def __init__(self):
        """初始化返回对象"""
        self._status_code = None
        self._reason = None
        self._elapsed = datetime.timedelta(0)
        self._value = None
        self._raw_value = None
        self._ok = False

    @property
    def value(self):
        return self._value

    @property
    def status_code(self) -> int:
        return self._status_code

    @property
    def reason(self) -> str|None:
        return self._reason

    @property
    def elapsed(self) -> datetime.timedelta:
        return self._elapsed

    @property
    def raw_value(self):
        return self._raw_value

    @property
    def ok(self) -> bool:
        return self._ok

    @reason.setter
    def reason(self, value):
        self._reason = value

    @status_code.setter
    def status_code(self, value: int):
        if not isinstance(value, int):
            raise ValueError("status_code must be an integer")

        if value < 0:
            raise ValueError("status_code must be >= 0")

        self._status_code = value

    @elapsed.setter
    def elapsed(self, value: datetime.timedelta):
        self._elapsed = value

    @value.setter
    def value(self, value):
        self._value = value

    @raw_value.setter
    def raw_value(self, value):
        self._raw_value = value

    @ok.setter
    def ok(self, value: bool):
        self._ok = value