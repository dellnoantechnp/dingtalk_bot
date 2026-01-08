import logging
from typing import Optional, Callable
from core.redis_client import get_redis_cluster
from dingtalk.Models.dingtalk_card_struct import DingTalkCardData

logger = logging.getLogger("dingtalk_bot")


class CardRepository:
    """
    负责 DingTalkCardData 对象的 Redis 存储、读取与原子更新
    """
    KEY_PREFIX = "dingtalk:card_data"
    EXPIRE_SECONDS = 86400 * 7    # 7 day

    @classmethod
    def _get_key(cls, out_track_id: str) -> str:
        return f"{cls.KEY_PREFIX}:{out_track_id}"

    @classmethod
    def _get_lock_key(cls, out_track_id: str) -> str:
        return f"lock:{cls.KEY_PREFIX}:{out_track_id}"

    @classmethod
    def save(cls, card_data: DingTalkCardData) -> bool:
        """保存对象（覆盖）
        :param card_data: DingTalkCardData
        :return: bool
        """
        if not card_data.out_track_id:
            logger.error("Save failed: out_track_id is missing")
            return False

        redis_client = get_redis_cluster()
        key = cls._get_key(card_data.out_track_id)

        try:
            # model_dump_json 会处理所有嵌套对象和 Enum
            json_str = card_data.model_dump_json(by_alias=True)
            logger.debug(f"Save data to redis key: {key}")
            redis_client.set(key, json_str, ex=cls.EXPIRE_SECONDS)
            return True
        except Exception as e:
            logger.error(f"Redis save error: {e}")
            return False

    @classmethod
    def load(cls, out_track_id: str) -> Optional[DingTalkCardData]:
        """读取对象"""
        redis_client = get_redis_cluster()
        key = cls._get_key(out_track_id)

        try:
            raw_data = redis_client.get(key)
            if not raw_data:
                return None
            return DingTalkCardData.model_validate_json(raw_data)
        except Exception as e:
            logger.error(f"Redis load error: {e}")
            return None

    @classmethod
    def atomic_update(cls, out_track_id: str, update_func: Callable[[DingTalkCardData], None]) -> Optional[
        DingTalkCardData]:
        """
        [核心方法] 并发安全的原子更新

        :param out_track_id: 卡片追踪ID
        :param update_func: 一个回调函数，接收当前对象，直接修改它。
                            例如: lambda data: data.card_parm_map.approve += 1
        :return: 更新后的最新对象，如果失败返回 None
        """
        redis_client = get_redis_cluster()
        lock_key = cls._get_lock_key(out_track_id)

        # 获取分布式锁 (timeout=5s 防止死锁, blocking_timeout=2s 等待锁的时间)
        # 注意：这里假设 redis_client (RedisCluster) 支持 lock 方法上下文
        try:
            with redis_client.lock(lock_key, timeout=5, blocking_timeout=2):
                # 1. 锁内读取 (Read)
                current_data = cls.load(out_track_id)
                if not current_data:
                    logger.warning(f"Update failed: Data not found for {out_track_id}")
                    return None

                # 2. 执行回调函数修改数据 (Modify)
                # 这里不需要返回值，直接修改引用对象即可
                try:
                    update_func(current_data)
                except Exception as logic_err:
                    logger.error(f"Update logic failed: {logic_err}")
                    return None

                # 3. 锁内写入 (Write)
                if cls.save(current_data):
                    return current_data
                return None

        except Exception as e:
            logger.error(f"Atomic update failed (Lock error?): {e}")
            return None