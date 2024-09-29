import argparse
import redis
import sys
import time
from humanfriendly import format_timespan
from typing import Union

from redis.exceptions import RedisClusterException

COUNT = 1000
DELETE_COUNT = 0

# 获取当前时间戳（毫秒）
current_time = int(time.time() * 1000)

# 获取2天前的时间戳（毫秒）
two_days_ago = current_time - 2 * 24 * 60 * 60 * 1000


def get_connect(host, port, password) -> redis.client.Redis:
    try:
        ## RedisCluster
        r = redis.RedisCluster(host=host, port=port, password=password)
    except RedisClusterException:
        ## Redis Standalone
        r = redis.Redis(host=host, port=port, password=password)
        keyspace = r.info(section="keyspace")
        if len(keyspace) > 1:
            print("Please choice one db id: ", file=sys.stderr)
            for db in keyspace:
                keys = keyspace.get(db).get("keys")
                print(" ", db.lstrip("db"), "  <-- total keys", keys, file=sys.stderr)
            print("input your select: ", file=sys.stderr, end="")
            select_db = input()
            r.select(select_db)
    return r


def check_scan_result(connect, match=None):
    for i in connect.scan_iter(match=match, count=COUNT):
        if has_ttl(connect=connect, key=i):
            try:
                if args.key_pattern:
                    key = i.decode()
                    # parts = key.split(":")
                    # if parts[2].isdigit():
                    #     timestamp = int(parts[1])
                    #     if timestamp < two_days_ago:
                    #         # print(f"Deleted key: {key}")
                    #         connect.delete(key)
                    #     else:
                    #         print(f"Within two days: {key}")
                    ## 获取 key_pattern 中所有 key 的 ttl 时间
                    ttl = connect.ttl(key)
                    human_ttl = format_timespan(ttl)
                    print(f"{key}  current_time_ts: {current_time}     expire_time: {human_ttl}")
                else:
                    print(i.decode())

            except Exception:
                print(repr(i), "RAW key name")


def check_scan_and_del_zset(connect: Union[redis.RedisCluster, redis.Redis], match=None):
    ten_day_ts = int(time.time() * 1000) - 10 * 86400000
    print("10 day ago timestamp:", ten_day_ts)
    for i in connect.scan_iter(match=match, count=COUNT):
        if len(connect.zrevrangebyscore(name=i, max=ten_day_ts, min=1)) > 0:
            print(f"remove key {i.decode()} item with score 1-{ten_day_ts}")
            connect.zremrangebyscore(name=i, max=ten_day_ts, min=1)
        else:
            print(f"new key {i.decode()}")


def has_ttl(connect: redis.client.Redis, key: bytes) -> bool:
    ret = connect.ttl(key)
    if ret > -1:
        return True
    else:
        return False


parser = argparse.ArgumentParser(
    description="Scan all keys with no-ttl in redis/redis-cluster.",
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument("-a", "--address", action="store", type=str, default="localhost", required=True,
                    help="设置redis连接地址, [default: localhost]")
parser.add_argument("-p", "--port", action="store", type=int, default=6379, help="设置redis的连接端口, [default: 6379]")
parser.add_argument("--password", action="store", type=int, default=None, help="设置redis的认证密码")
parser.add_argument("-k", "--key-pattern", action="store", type=str, default="*", help="设置 Key 的名称模式, [default: *]\n"
                                                                                       "example:\n"
                                                                                       "  authToken*\n"
                                                                                       "  *\n")
parser.add_argument("--rm-zset-item", action="store", type=bool, default=False,
                    help="清理 zset 过期 item  [default: false]")
args = parser.parse_args()

try:
    if __name__ == "__main__":
        r = get_connect(host=args.address, port=args.port, password=args.password)
        if args.rm_zset_item:
            check_scan_result(r, args.key_pattern)
            # check_scan_and_del_zset(r, args.key_pattern)
        else:
            check_scan_result(r, args.key_pattern)
except (Exception, KeyboardInterrupt):
    pass
