import datetime


class RedisDataResponse:
    """
    Redis Response Object
    """
    __attrs__ = [
        "status_code",
        "reason",
        "elapsed",
        "value",
        "raw_value",
        "ok",
        "key",
        "field",
    ]

    def __init__(self):
        """
        初始化返回对象
        :field key:  redis key name
        :field status_code:  redis status_code
        :field reason:  redis response reason text
        :field elapsed:  redis elapsed time
        :field value:   redis value text
        :field raw_value:  redis raw_value text
        :field ok:  redis ok flag
        :field field: redis hset key field name
        """
        self._key = None
        self._status_code = None
        self._reason = None
        self._elapsed = datetime.timedelta(0)
        self._value = None
        self._raw_value = None
        self._ok = False
        self._field = None

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
        if self.status_code >= 50000:
            self._ok = False
        else:
            self._ok = True
        return self._ok

    @property
    def key(self) -> str:
        return self._key

    @property
    def field(self) -> str:
        return self._field

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

    @key.setter
    def key(self, key):
        self._key = key

    @field.setter
    def field(self, field):
        self._field = field