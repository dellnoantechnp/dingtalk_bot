import sys
from alibabacloud_dingtalk.oauth2_1_0.client import Client as dingtalkoauth2_1_0Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dingtalk.oauth2_1_0 import models as dingtalkoauth_2__1__0_models
from alibabacloud_tea_util.client import Client as UtilClient


class Dingtalk_Base:
    def __init__(self, appKey=None, appSecret=None):
        self.appKey = appKey
        self.appSecret = appSecret

    # @staticmethod
    def create_client(self) -> dingtalkoauth2_1_0Client:
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
    #         app_key='dingqkoo0gpksjflc7ih',
    #         app_secret='utI4JAsz0bZonfiIybwghmE_jf9i3a6dpyQQVsB9qlirIq9h_Sw50qkOzvuMVdPj'
    #     )
    #     try:
    #         token_resp = client.get_access_token(get_access_token_request)
    #         return token_resp.body.access_token
    #     except Exception as err:
    #         if not UtilClient.empty(err.code) and not UtilClient.empty(err.message):
    #             # err 中含有 code 和 message 属性，可帮助开发定位问题
    #             pass

    def getAccessToken(self) -> str:
        client = self.create_client()
        get_access_token_request = dingtalkoauth_2__1__0_models.GetAccessTokenRequest(
            app_key=self.appKey,
            app_secret=self.appSecret
        )
        try:
            token_resp = client.get_access_token(get_access_token_request)
            return token_resp.body.access_token
        except Exception as err:
            if not UtilClient.empty(err.code) and not UtilClient.empty(err.message):
                # err 中含有 code 和 message 属性，可帮助开发定位问题
                pass
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
    token = Dingtalk_Base.main(sys.argv[1:])
    print(token)