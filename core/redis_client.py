from rediscluster import RedisCluster
from django.conf import settings

_redis_cluster = None


def get_redis_cluster():
    global _redis_cluster
    if _redis_cluster is None:
        _redis_cluster = RedisCluster(
            startup_nodes=settings.REDIS_CLUSTER_NODES,
            decode_responses=True,
            skip_full_coverage_check=True,
            password="123.com"  ## redis 密码
        )
    return _redis_cluster
