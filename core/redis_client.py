import redis
from redis import RedisCluster, Redis, ConnectionPool
from django.conf import settings
import logging
from core.RedisDataResponse import RedisDataResponse
from utils.elapsed import timer
from django_redis.client import DefaultClient

_redis = None
logger = logging.getLogger("dingtalk_bot")


# Deprecated
# Custom Redis Cluster Client
# For example::
#
#     redis://[[username]:[password]]@localhost:6379/0
#     rediss://[[username]:[password]]@localhost:6379/0
#     unix://[username@]/path/to/socket.sock?db=0[&password=password]
class CustomRedisCluster(DefaultClient):

    def connect(self, index: int = 0):
        """Override the connection retrival function."""
        logger.debug(msg=f"Connect to redis cluster [{self._server}] ...")
        return RedisCluster.from_url(self._server[index])


def get_redis_cluster() -> Redis:
    global _redis
    if _redis is None:
        try:
            _pool = ConnectionPool.from_url(
                url=settings.REDIS_URL,
                decode_responses=True,
                #require_full_coverage=True,
                max_connections=10,
            )
            _redis = redis.Redis.from_pool(connection_pool=_pool)
            logger.info(f"Redis client initialized successfully with URL: {settings.REDIS_URL}, "
                        f"pool size is {_redis.connection_pool._created_connections}/{_pool.max_connections}")
        except Exception as e:
            logger.error(msg=f"Redis client initialized failed with exception: {e}")
            raise e
    return _redis


def redis_set(key: str, value: str, timeout=7000) -> RedisDataResponse:
    """
    redis 设置基本字符串 key
    """
    logger.debug(msg=f"Set redis key [{key}] ...")

    result = RedisDataResponse()
    # 计算耗时
    with timer() as t:
        ret = get_redis_cluster().set(key, value, timeout)
        result.raw_value = ret
        result.value = ret

    result.elapsed = t['elapsed']
    result.key = key
    if ret:
        result.status_code = 10000
    else:
        result.status_code = 50000
        result.reason = "data store failed"
    logger.debug(msg=f"Set redis key [{key}] done, use_time={result.elapsed.total_seconds() * 1000:.2f}ms  status_code={result.status_code} value={value}")
    return result


def redis_get(key) -> RedisDataResponse:
    """
    redis 读取基本字符串
    :return: RedisDataResponse
    """
    logger.debug(msg=f"Read redis key [{key}] ...")

    result = RedisDataResponse()
    with timer() as t:
        ret = get_redis_cluster().get(key)
        result.raw_value = ret
        result.value = ret

    result.elapsed = t['elapsed']
    result.key = key
    if ret:
        result.status_code = 10000
    else:
        result.status_code = 50000
        result.reason = "data not found"
    logger.debug(msg=f"Read redis key [{key}] done, use_time={result.elapsed.total_seconds() * 1000:.2f}ms status_code={result.status_code} value={ret}")
    return result


def redis_hset(key: str, mapping: dict, timeout=7000) -> RedisDataResponse:
    """redis hset"""
    logger.debug(msg=f"Set redis hset key [{key}] to [{repr(mapping)}]")
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

    result.elapsed = t['elapsed']
    result.key = key
    logger.debug(msg=f"Set redis hset key [{key}] done, use_time={result.elapsed.total_seconds() * 1000:.2f}ms status_code={result.status_code} value={ret}")
    return result


def redis_hget(key: str, field: str) -> RedisDataResponse:
    """redis hget single field"""
    logger.debug(msg=f"Read redis hash key [{key}].[{field}] ...")
    result = RedisDataResponse()

    with timer() as t:
        ret = get_redis_cluster().hget(name=key, key=field)
        result.raw_value = ret
        result.value = ret

    result.elapsed = t['elapsed']
    result.key = key
    result.field = field
    if ret:
        result.status_code = 10000
    else:
        result.status_code = 50000
        result.reason = "data not found"
    logger.debug(msg=f"Get redis hset key [{key}].[{field}] done, use_time={result.elapsed.total_seconds() * 1000:.2f}ms status_code={result.status_code} value={ret}")
    return result


def redis_hgetall(key: str) -> RedisDataResponse:
    """redis hget all fields"""
    logger.debug(msg=f"Read redis hash key [{key}] ...")
    result = RedisDataResponse()

    with timer() as t:
        ret = get_redis_cluster().hgetall(name=key)
        result.raw_value = ret
        result.value = ret

    result.elapsed = t['elapsed']
    result.key = key
    if len(ret.keys()) > 0:
        result.status_code = 10000
    else:
        result.status_code = 50000
        result.reason = "data not found"
    logger.debug(msg=f"Get redis hset key [{key}] done, use_time={result.elapsed.total_seconds() * 1000:.2f}ms status_code={result.status_code} value={ret}")
    return result
