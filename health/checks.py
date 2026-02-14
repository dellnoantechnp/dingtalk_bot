from django.http import HttpResponse
import logging

from core.redis_client import redis_set

logger = logging.getLogger("dingtalk_bot")


def check_live():
    try:
        ret = redis_set(key="health:live", value="1", timeout=2)
        return ret.ok
    except Exception as e:
        logger.error(f"Error: health check live failed, msg={e}")
        raise e