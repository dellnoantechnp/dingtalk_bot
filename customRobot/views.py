import alibabacloud_dingtalk.im_1_0.models
from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponse
import dingtalk_stream
from . import EchoMarkdownHandler
from dingtalk.Dingtalk_Base import Dingtalk_Base
from dingtalk.Card import Card, CardData
from django.views.decorators.csrf import csrf_exempt
import logging
import time
import os

from alibabacloud_dingtalk.im_1_0 import models as dingtalkim__1__0_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dingtalk.im_1_0.client import Client as dingtalkim_1_0Client
from alibabacloud_dingtalk.card_1_0.client import Client as dingtalkcard_1_0Client
from alibabacloud_tea_util import models as util_models

from alibabacloud_dingtalk.card_1_0 import models as dingtalkcard__1__0_models

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

def create_imclient() -> dingtalkim_1_0Client:
    """
    使用 Token 初始化账号Client
    @return: Client
    @throws Exception
    """
    config = open_api_models.Config()
    config.protocol = 'https'
    config.region_id = 'central'
    return dingtalkim_1_0Client(config)

def create_card_client() -> dingtalkcard_1_0Client:
    """
    使用 Token 初始化账号Client
    @return: Client
    @throws Exception
    """
    config = open_api_models.Config()
    config.protocol = 'https'
    config.region_id = 'central'
    return dingtalkcard_1_0Client(config)

@csrf_exempt
def dingtalk_test(request):
    logger = logging.getLogger("dingtalk_bot")
    logger.debug("appKey:" + request.POST.get("appKey") + " appSecret:" + request.POST.get("appSecret"))
    dd = Dingtalk_Base(request.POST.get("appKey"), request.POST.get("appSecret"))
    token = dd.get_access_token()
    logger.info("token: " + token)
    time_tag = int(time.time() * 1000)
    #card_template_id = "bd57beb1-d127-45e5-92d4-81277c59c87b.schema"
    card_template_id = "98a61096-31e1-4611-be4e-b1d2f6897225.schema"
    out_track_id = f"{card_template_id}.{time_tag}"

    send_interactive_card_headers = dingtalkim__1__0_models.SendInteractiveCardHeaders()
    send_interactive_card_headers.x_acs_dingtalk_access_token = token

    send_interactive_card_request = dingtalkim__1__0_models.SendInteractiveCardRequest()
    send_interactive_card_request.card_template_id = card_template_id
    # send_interactive_card_request.card_template_id = "b2a8bb23-0b04-45c7-8686-e3668b082ed8.schema"
    # send_interactive_card_request.out_track_id = "b2a8bb23-0b04-45c7-8686-e3668b082ed8.schema.1715069378009"
    send_interactive_card_request.out_track_id = out_track_id
    send_interactive_card_request.robot_code = "dingqkoo0gpksjflc7ih"
    send_interactive_card_request.open_conversation_id = "cidUQXUpOwFEbiRNp87JyFE3w=="
    send_interactive_card_request.conversation_type = 1

    card_data = dingtalkim__1__0_models.SendInteractiveCardRequestCardData()
    object_string = {
      "markdown_content": "#### Tiltle\n* 123\n* 456",
      "approve_count": 10,
      "reject_count": 3,
      "card_title": "本次发布更新",
      "markdown_title": "本周发布commit汇总",
      "markdown": "4567"
    }.__str__()
    card_data.card_param_map = {"title": "朱小志提交的财务报销", "detailUrl": "https://dingtalk.com", "status": "pending", "sys_full_json_obj": object_string}
    card_data.card_media_id_param_map = {}
    # send_interactive_card_request.card_data = dingtalkim__1__0_models.InteractiveCardCreateInstanceRequestCardData({"title": "123", "detailUrl": "https://dingtalk.com", "status": "pending", "sys_ful_json_obj": "{}"})
    # send_interactive_card_request.card_data = {"cardParamMap": {"title": "朱小志提交的财务报销", "detailUrl": "https://dingtalk.com", "status": "pending", "sys_full_json_obj": "{}"}}
    send_interactive_card_request.card_data = card_data

    ## Card
    create_and_deliver_headers = dingtalkcard__1__0_models.CreateAndDeliverHeaders()
    create_and_deliver_headers.x_acs_dingtalk_access_token = dd.get_access_token()
    create_and_deliver_request = dingtalkcard__1__0_models.CreateAndDeliverRequest()
    create_and_deliver_request.card_template_id = card_template_id
    # send_interactive_card_request.card_template_id = "b2a8bb23-0b04-45c7-8686-e3668b082ed8.schema"
    # send_interactive_card_request.out_track_id = "b2a8bb23-0b04-45c7-8686-e3668b082ed8.schema.1715069378009"
    create_and_deliver_request.out_track_id = out_track_id
    create_and_deliver_request.robot_code = "dingqkoo0gpksjflc7ih"
    create_and_deliver_request.open_conversation_id = "cidUQXUpOwFEbiRNp87JyFE3w=="
    create_and_deliver_request.conversation_type = 1
    create_and_deliver_request.open_space_id = "dtv1.card//IM_SINGLE.cidUQXUpOwFEbiRNp87JyFE3w=="
    create_and_deliver_request.callback_type = "STREAM"
    #create_and_deliver_request.callback_type = "HTTP"

    im_group_deliver_model = dingtalkcard__1__0_models.CreateAndDeliverRequestImGroupOpenDeliverModel()
    im_group_deliver_model.robot_code = "dingqkoo0gpksjflc7ih"
    im_group_open_space_model = dingtalkcard__1__0_models.CreateCardRequestImGroupOpenSpaceModel()
    im_group_open_space_model.support_forward = True

    create_and_deliver_request.im_group_open_deliver_model = im_group_deliver_model
    create_and_deliver_request.im_group_open_space_model = im_group_open_space_model
    create_and_deliver_request.card_data = card_data

    logger.warning(send_interactive_card_request.from_map())

    im_client = create_imclient()
    card_client = create_card_client()
    try:
        logger.info("卡片创建和投递")
        resp: dingtalkcard__1__0_models.CreateAndDeliverResponse = card_client.create_and_deliver_with_options(
            create_and_deliver_request,
            create_and_deliver_headers,
            util_models.RuntimeOptions()
        )

        logger.info("卡片消息投递到聊天")
        resp: dingtalkim__1__0_models.SendInteractiveCardResponse = im_client.send_interactive_card_with_options(
            send_interactive_card_request,
            send_interactive_card_headers,
            util_models.RuntimeOptions()
        )
    except Exception as err:
        logger.error(err)

    # 更新卡片内容
    try:
        time.sleep(5)
        update_card_data = dingtalkim__1__0_models.SendInteractiveCardRequestCardData()
        object_string = {
            "markdown_content": "#### Tiltle\n* 123\n* 456556",
            "approve_count": 10,
            "reject_count": 3,
            "card_title": "本次发布更新",
            "markdown_title": "本周发布commit汇总",
            "markdown": "4567888888888"
        }.__str__()
        update_card_data.card_param_map = {"title": "朱小志提交的财务报销", "detailUrl": "https://dingtalk.com",
                                    "status": "pending", "sys_full_json_obj": object_string}
        update_card_data.card_media_id_param_map = {}

        logger.info("卡片更新")
        update_card_request = dingtalkcard__1__0_models.UpdateCardRequest()
        update_card_request.out_track_id = out_track_id
        update_card_request.card_data = update_card_data

        update_card_header = dingtalkcard__1__0_models.UpdateCardHeaders()
        update_card_header.x_acs_dingtalk_access_token = token
        resp: dingtalkcard__1__0_models.UpdateCardResponse = card_client.update_card_with_options(
            update_card_request,
            update_card_header,
            util_models.RuntimeOptions()
        )

        update_interactive_card_request = dingtalkim__1__0_models.UpdateInteractiveCardRequest()
        update_interactive_card_request.card_template_id = card_template_id
        # send_interactive_card_request.card_template_id = "b2a8bb23-0b04-45c7-8686-e3668b082ed8.schema"
        # send_interactive_card_request.out_track_id = "b2a8bb23-0b04-45c7-8686-e3668b082ed8.schema.1715069378009"
        #update_interactive_card_request.out_track_id = out_track_id + ".update"
        update_interactive_card_request.robot_code = "dingqkoo0gpksjflc7ih"
        update_interactive_card_request.open_conversation_id = "cidUQXUpOwFEbiRNp87JyFE3w=="
        update_interactive_card_request.conversation_type = 1
        update_interactive_card_request.card_data = update_card_data

        update_interactive_card_headers = dingtalkim__1__0_models.UpdateInteractiveCardHeaders()
        update_interactive_card_headers.x_acs_dingtalk_access_token = token

        logger.info("卡片更新投递到聊天")
        resp: dingtalkim__1__0_models.UpdateInteractiveCardResponse = im_client.update_interactive_card_with_options(
            update_interactive_card_request,
            update_interactive_card_headers,
            util_models.RuntimeOptions()
        )
    except Exception as err:
        pass

    # return HttpResponse(dd.getAccessToken())

    return HttpResponse(resp.body)


@csrf_exempt
def interactive_card_test(request):
    logger = logging.getLogger("dingtalk_bot")
    logger.debug("appKey:" + request.POST.get("appKey") + " appSecret:" + request.POST.get("appSecret"))
    dd = Dingtalk_Base(request.POST.get("appKey"), request.POST.get("appSecret"))
    token = dd.get_access_token()
    logger.info("token: " + token)

    a = Card(access_token=token,
             card_template_id="98a61096-31e1-4611-be4e-b1d2f6897225.schema",
             robot_code="dingqkoo0gpksjflc7ih",
             open_conversation_id="cidUQXUpOwFEbiRNp87JyFE3w==",
             )
    card_vars = {
        "markdown_content": "#### Tiltle\n* 123\n* 456",
        "approve_count": 10,
        "reject_count": 3,
        "card_title": "本次发布更新",
        "markdown_title": "本周发布commit汇总",
        "markdown": "4567121231231"
    }
    b = CardData(card_vars)
    a.create_and_update_card_data(b)
    a.send_interactive_card()

    time.sleep(3)
    card_vars["markdown_content"] = card_vars["markdown_content"] + "7890"
    b = CardData(card_vars)
    #logger.info(f"Card param map: {b.get_card_content()}")
    a.create_and_update_card_data(b)
    #a.__persistent_card()

    logger.info(f"开始更新卡片")
    a.update_interactive_card()
    return HttpResponse("OK")


@csrf_exempt
def interactive_card_test2(request):
    logger = logging.getLogger("dingtalk_bot")
    logger.debug(f"appKey: {os.environ.get('DINGTALK_CLIENT_ID')} appSecret: {os.environ.get('DINGTALK_CLIENT_SECRET')}")
    dd = Dingtalk_Base(os.environ.get("DINGTALK_CLIENT_ID"), os.environ.get("DINGTALK_CLIENT_SECRET"), "dingtalk_bot")
    token = dd.get_access_token()
    logger.info("token: " + token)

    a = Card(access_token=token,
             card_template_id="98a61096-31e1-4611-be4e-b1d2f6897225.schema",
             robot_code="dingqkoo0gpksjflc7ih",
             open_conversation_id="cidUQXUpOwFEbiRNp87JyFE3w==",
             )
    card_vars = {
        "markdown_content": "#### Tiltle\n* 123\n* 456",
        "approve_count": 10,
        "reject_count": 3,
        "card_title": "本次发布更新",
        "markdown_title": "本周发布commit汇总",
        "markdown": "4567121231231"
    }
    b = CardData(card_vars)
    a.create_and_update_card_data(b)
    a.send_interactive_card()

    time.sleep(3)
    card_vars["markdown_content"] = card_vars["markdown_content"] + "7890"
    b = CardData(card_vars)
    #logger.info(f"Card param map: {b.get_card_content()}")
    a.create_and_update_card_data(b)
    #a.__persistent_card()

    logger.info(f"开始更新卡片")
    a.update_interactive_card()
    return HttpResponse("OK")