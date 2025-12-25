import time

from rediscluster import RedisCluster
from django.conf import settings
import logging
from core.RedisDataResponse import RedisDataResponse
from utils.elapsed import timer

_redis_cluster = None


def get_redis_cluster() -> RedisCluster:
    global _redis_cluster
    if _redis_cluster is None:
        _redis_cluster = RedisCluster(
            startup_nodes=settings.REDIS_CLUSTER_NODES,
            decode_responses=True,
            skip_full_coverage_check=True,
            password=settings.REDIS_PASSWORD  # redis 密码
        )
    return _redis_cluster


def redis_set(key: str, value: str, timeout=7000) -> RedisDataResponse:
    """
    redis 设置基本字符串 key
    """
    logging.debug(msg=f"Set redis key [{key}] ...")

    result = RedisDataResponse()
    # 计算耗时
    with timer() as t:
        ret = get_redis_cluster().set(key, value, timeout)
        result.raw_value = ret
        result.value = ret

    result.elapsed = t['elapsed']
    if ret:
        result.status_code = 10000
    else:
        result.status_code = 50000
        result.reason = "data store failed"
    logging.debug(msg=f"Set redis key [{key}] done, use_time={result.elapsed.total_seconds() * 1000:.2f}ms  status_code={result.status_code} value={value}")
    return result


def redis_get(key) -> RedisDataResponse:
    """
    redis 读取基本字符串
    :return: token_string
    """
    logging.debug(msg=f"Read redis key [{key}] ...")

    result = RedisDataResponse()
    with timer() as t:
        ret = get_redis_cluster().get(key)
        result.raw_value = ret
        result.value = ret

    result.elapsed = t['elapsed']
    if ret:
        result.status_code = 10000
    else:
        result.status_code = 50000
        result.reason = "data not found"
    logging.debug(msg=f"Read redis key [{key}] done, use_time={result.elapsed.total_seconds() * 1000:.2f}ms status_code={result.status_code} value={ret}")
    return result


def redis_hset(key: str, mapping: dict, timeout=7000) -> RedisDataResponse:
    """redis hset"""
    logging.debug(msg=f"Set redis hset key [{key}] to [{repr(mapping)}]")
    result = RedisDataResponse()

    with timer() as t:
        ret = get_redis_cluster().hset(name=key, mapping=mapping)
        result.raw_value = ret
        result.value = ret
        if ret >= 0:
            # redis_client.hset ret 0: update exists item
            # redis_client.hset ret 1: update or create a key, add 1 item
            # redis_client.hset ret more than 1: update or create a key, add more item
            get_redis_cluster().execute_command('expire', key, timeout)
            result.status_code = 10000
        else:
            result.status_code = 50000
            result.reason = "data store failed"

    result.elapsed = t.elapsed
    logging.debug(msg=f"Set redis hset key [{key}] done, use_time={result.elapsed.total_seconds() * 1000:.2f}ms status_code={result.status_code} value={ret}")
    return result


def redis_hget(key: str, field: str) -> RedisDataResponse:
    """redis hget single field"""
    logging.debug(msg=f"Read redis hash key [{key}].[{field}] ...")
    result = RedisDataResponse()

    with timer() as t:
        ret = get_redis_cluster().hget(name=key, key=field)
        result.raw_value = ret
        result.value = ret

    result.elapsed = t['elapsed']
    if ret:
        result.status_code = 10000
    else:
        result.status_code = 50000
        result.reason = "data not found"
    logging.debug(msg=f"Get redis hset key [{key}].[{field}] done, use_time={result.elapsed.total_seconds() * 1000:.2f}ms status_code={result.status_code} value={ret}")
    return result

def redis_hgetall(key: str) -> RedisDataResponse:
    """redis hget all fields"""
    logging.debug(msg=f"Read redis hash key [{key}] ...")
    result = RedisDataResponse()

    with timer() as t:
        ret = get_redis_cluster().hgetall(name=key)
        result.raw_value = ret
        result.value = ret

    result.elapsed = t['elapsed']
    if len(ret.keys()) > 0:
        result.status_code = 10000
    else:
        result.status_code = 50000
        result.reason = "data not found"
    logging.debug(msg=f"Get redis hset key [{key}] done, use_time={result.elapsed.total_seconds() * 1000:.2f}ms status_code={result.status_code} value={ret}")
    return result
