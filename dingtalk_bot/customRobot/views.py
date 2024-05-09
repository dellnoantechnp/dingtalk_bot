import alibabacloud_dingtalk.im_1_0.models
from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponse
import dingtalk_stream
from . import EchoMarkdownHandler
import dingtalk.Dingtalk_Base
from django.views.decorators.csrf import csrf_exempt
import logging

from alibabacloud_dingtalk.im_1_0 import models as dingtalkim__1__0_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dingtalk.im_1_0.client import Client as dingtalkim_1_0Client
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

def index(request):
    return JsonResponse({"foo": "bar"})


def setup_logger():
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('%(asctime)s %(name)-8s %(levelname)-8s %(message)s [%(filename)s:%(lineno)d]'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

## 示例：https://github.com/open-dingtalk/dingtalk-tutorial-python
def dingtalk_stream1(request):
    logger = setup_logger()

    credential = dingtalk_stream.Credential("dino0gpks7ih", "utI4JqkOzvuj")
    client = dingtalk_stream.DingTalkStreamClient(credential)
    client.register_callback_handler(dingtalk_stream.chatbot.ChatbotMessage.TOPIC, EchoMarkdownHandler.EchoMarkdownHandler(logger))
    client.start_forever()

def create_client() -> dingtalkim_1_0Client:
    """
    使用 Token 初始化账号Client
    @return: Client
    @throws Exception
    """
    config = open_api_models.Config()
    config.protocol = 'https'
    config.region_id = 'central'
    return dingtalkim_1_0Client(config)
@csrf_exempt
def dingtalk_test(request):
    logger = setup_logger()
    logger.info(request.POST.get("appKey") + "_" + request.POST.get("appSecret"))
    dd = dingtalk.Dingtalk_Base.Dingtalk_Base(request.POST.get("appKey"), request.POST.get("appSecret"))
    token = dd.getAccessToken()
    logger.info("token: " + token)

    send_interactive_card_headers = dingtalkim__1__0_models.SendInteractiveCardHeaders()
    send_interactive_card_headers.x_acs_dingtalk_access_token = token

    send_interactive_card_request = dingtalkim__1__0_models.SendInteractiveCardRequest()
    send_interactive_card_request.card_template_id = "bd57beb1-d127-45e5-92d4-81277c59c87b.schema"
    # send_interactive_card_request.card_template_id = "b2a8bb23-0b04-45c7-8686-e3668b082ed8.schema"
    # send_interactive_card_request.out_track_id = "b2a8bb23-0b04-45c7-8686-e3668b082ed8.schema.1715069378009"
    send_interactive_card_request.out_track_id = "bd57beb1-d127-45e5-92d4-81277c59c87b.schema.1715223748128"
    send_interactive_card_request.robot_code = "dingqkoo0gpksjflc7ih"
    send_interactive_card_request.open_conversation_id = "cidUQXUpOwFEbiRNp87JyFE3w=="
    send_interactive_card_request.conversation_type = 1

    card_data = dingtalkim__1__0_models.SendInteractiveCardRequestCardData()
    object_string = {
  "markdown_content": "#### Tiltle\n* 123\n* 456",
  "approve_count": 4,
  "reject_count": 1,
  "card_title": "本次发布更新",
  "markdown_title": "本周发布commit汇总",
  "markdown": "456"
}.__str__()
    card_data.card_param_map = {"title": "朱小志提交的财务报销", "detailUrl": "https://dingtalk.com", "status": "pending", "sys_full_json_obj": object_string}
    card_data.card_media_id_param_map = {}
    # send_interactive_card_request.card_data = dingtalkim__1__0_models.InteractiveCardCreateInstanceRequestCardData({"title": "123", "detailUrl": "https://dingtalk.com", "status": "pending", "sys_ful_json_obj": "{}"})
    # send_interactive_card_request.card_data = {"cardParamMap": {"title": "朱小志提交的财务报销", "detailUrl": "https://dingtalk.com", "status": "pending", "sys_full_json_obj": "{}"}}
    send_interactive_card_request.card_data = card_data

    # logger.warn(send_interactive_card_request.from_map())

    client = create_client()
    try:
        send_interactive_card_request.validate()
        resp: dingtalkim__1__0_models.SendOTOInteractiveCardResponse = client.send_interactive_card_with_options(send_interactive_card_request, send_interactive_card_headers, util_models.RuntimeOptions())
    except Exception as err:
        logger.error(err)


    # return HttpResponse(dd.getAccessToken())
    return HttpResponse(resp.body)

