import redis
from redis import RedisCluster
import time

# 初始化Redis集群连接
startup_nodes = [
    {"host": "127.0.0.1", "port": "7000"},
    {"host": "127.0.0.1", "port": "7001"},
    {"host": "127.0.0.1", "port": "7002"},
]
rc = RedisCluster(startup_nodes=startup_nodes, decode_responses=True)

# 获取当前时间戳（毫秒）
current_time = int(time.time() * 1000)

# 获取2天前的时间戳（毫秒）
two_days_ago = current_time - 2 * 24 * 60 * 60 * 1000

# 扫描并删除旧的key
def delete_old_keys(prefix="im_user_hot_data:"):
    #cursor = 0
    while True:
        cursor, keys = rc.scan(match=f"{prefix}*", count=1000)
        for key in keys:
            try:
                # 假设key是以 "im_user_hot_data:{timestamp}" 的格式命名的
                parts = key.split(":")
                if parts[2].isdigit():
                    timestamp = int(parts[1])
                    if timestamp < two_days_ago:
                        # rc.delete(key)
                        print(f"Deleted key: {key}")
            except ValueError:
                print(f"Skipping key with unexpected format: {key}")

        # if cursor == 0:
        #     break

# 运行脚本
if __name__ == "__main__":
    delete_old_keys()
