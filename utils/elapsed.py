import datetime
import time
from contextlib import contextmanager



@contextmanager
def timer():
    start = time.monotonic()
    # 这里的 data 字典用于在上下文内外传递结果
    metrics = {}
    yield metrics
    end = time.monotonic()
    metrics['elapsed'] = datetime.timedelta(seconds=end - start)
