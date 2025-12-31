import logging
import sys
from alibabacloud_dingtalk.oauth2_1_0.client import Client as dingtalkoauth2_1_0Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dingtalk.oauth2_1_0 import models as dingtalkoauth_2__1__0_models
from alibabacloud_tea_util.client import Client as UtilClient
from logging import Logger
from typing import Union, Optional
# from django.core.cache import caches
from django.core.cache.backends.redis import RedisCacheClient

from core.redis_client import get_redis_cluster, redis_set, redis_get


class DingtalkBase:
    def __init__(self, app_key: Union[str] = "", app_secret: Union[str] = "", logger_name: Optional[str] = None):
        self.logger = None
        self.appKey = app_key
        self.appSecret = app_secret
        self._client = None
        self.initial_logger(logger=logger_name)
        self.token_redis_key_name = "dingtalk_bot_token_" + app_key

    def initial_logger(self, logger):
        if logger:
            self.logger = logging.getLogger(logger)
        else:
            self.logger = logging.getLogger("dingtalk_bot")

    @property
    def client(self) -> dingtalkoauth2_1_0Client:
        """
        使用 Token 初始化账号Client
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config()
        config.protocol = 'https'
        config.region_id = 'central'
        return dingtalkoauth2_1_0Client(config)

    # @staticmethod
    # def main(
    #     args: List[str],
    # ) -> None:
    #     client = Sample.create_client()
    #     get_access_token_request = dingtalkoauth_2__1__0_models.GetAccessTokenRequest(
    #         app_key='',
    #         app_secret=''
    #     )
    #     try:
    #         token_resp = client.get_access_token(get_access_token_request)
    #         return token_resp.body.access_token
    #     except Exception as err:
    #         if not UtilClient.empty(err.code) and not UtilClient.empty(err.message):
    #             # err 中含有 code 和 message 属性，可帮助开发定位问题
    #             pass

    @property
    def access_token(self) -> str:
        get_access_token_request = dingtalkoauth_2__1__0_models.GetAccessTokenRequest(
            app_key=self.appKey,
            app_secret=self.appSecret
        )
        try:
            result = redis_get(self.token_redis_key_name)
            if result.ok:
                self.logger.debug(msg=f"Load token from redis is [{result.value}]...")
                return result.value
            else:
                token_resp = self.client.get_access_token(get_access_token_request)
                self.logger.info(f"Renew token: {token_resp.body.access_token}")
                api_token = token_resp.body.access_token
                redis_set(key=self.token_redis_key_name, value=api_token)
                return api_token
        except Exception as err:
            if not UtilClient.empty(err.code) and not UtilClient.empty(err.message):
                # err 中含有 code 和 message 属性，可帮助开发定位问题
                self.logger.error(msg="Request dingtalk api to get access_token error.")
            raise err

    # def __get_redis_client(self) -> RedisCacheClient:
    #     """
    #     返回 redis_client
    #
    #     :return: redis_client
    #     """
    #     self.redis_client = get_redis_cluster()
    #     # if not hasattr(self, "redis_client"):
    #     #     redis_cache = caches["default"]
    #     #     redis_client = redis_cache.client.get_client()
    #     #     self.redis_client = redis_client
    #     return self.redis_client

    # def redis_hset(self, key: str, value: dict) -> bool:
    #     """
    #     redis 设置 hset key
    #
    #     :return: True / False
    #     """
    #     return self.__get_redis_client().hset(name=key,
    #                                           mapping=value) >= 0

    # @staticmethod
    # async def main_async(
    #     args: List[str],
    # ) -> None:
    #     client = Sample.create_client()
    #     get_access_token_request = dingtalkoauth_2__1__0_models.GetAccessTokenRequest(
    #         app_key='dingeqqpkv3xxxxxx',
    #         app_secret='GT-lsu-taDAxxxsTsxxxx'
    #     )
    #     try:
    #         result = await client.get_access_token_async(get_access_token_request)
    #         return result.body.access_token
    #     except Exception as err:
    #         if not UtilClient.empty(err.code) and not UtilClient.empty(err.message):
    #             # err 中含有 code 和 message 属性，可帮助开发定位问题
    #             pass


if __name__ == '__main__':
    token = DingtalkBase.main(sys.argv[1:])
    print(token)
