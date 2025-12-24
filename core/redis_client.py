from rediscluster import RedisCluster
from django.conf import settings
import logging
from core.RedisDataResponse import RedisDataResponse
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
    logging.debug(msg=f"Set redis key [{key}] to [{value}]")
    set_status = get_redis_cluster().set(key, value, timeout)
    if set_status >= 0:
        result = RedisDataResponse()
    return set_status

def redis_get(key) -> str:
    """
    redis 读取基本字符串
    :return: token_string
    """
    logging.debug(msg=f"Read redis key [{key}] ...")
    result = get_redis_cluster().get(key)
    logging.debug(msg=f"Read redis key [{key}] done, value [{result}]")
    if result:
        return result
    else:
        return ""

def redis_hset(key: str, mapping: dict, timeout=7000) -> bool:
    """redis hset"""
    logging.debug(msg=f"Set redis hset key [{key}] to [{repr(mapping)}]")
    status = get_redis_cluster().hset(name=key, mapping=mapping)
    if status >= 0:
        # redis_client.hset ret 0: update exists item
        # redis_client.hset ret 1: update or create a key, add 1 item
        # redis_client.hset ret more than 1: update or create a key, add more item
        get_redis_cluster().execute_command('expire', key, timeout)
        return True
    else:
        return False

def redis_hget_field(name: str, key: str) -> str:
    """redis hget"""
    logging.debug(msg=f"Read redis hash key [{name}].[{key}] ...")
    result = get_redis_cluster().hget(name=name, key=key)
    if result > 0:
        return result
    else:
        return ""