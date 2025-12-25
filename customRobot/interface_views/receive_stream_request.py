from dingtalk.DingtalkBase import DingtalkBase
from django.views.decorators.csrf import csrf_exempt
from dingtalk.Card import Card
from dingtalk.CardData import CardData
# from dingtalk.PrivateCardData import PrivateCardData
import logging
import time
import os
from django.http.response import JsonResponse, HttpResponse
from django.core.cache import caches
import json

logger_name = "dingtalk_bot"


@csrf_exempt
def receive_stream_request(request):
    logger = logging.getLogger(logger_name)
    logger.debug(
        f"appKey: {os.environ.get('DINGTALK_CLIENT_ID')} appSecret: {os.environ.get('DINGTALK_CLIENT_SECRET')}")
    dd = DingtalkBase(os.environ.get("DINGTALK_CLIENT_ID"), os.environ.get("DINGTALK_CLIENT_SECRET"), logger_name)
    token = dd.access_token
    receive_out_track_id = request.POST.get("outTrackId")
    logger.info(f"request parma outTrackId: {receive_out_track_id} from CorpId: {request.POST.get('corpId')}")

    # redis_cache = caches["default"]
    # redis_client = redis_cache.client.get_client()
    # previous_card = redis_client.hgetall(receive_out_track_id)

    # logger.info(request.POST.get("TOPIC"))
    a = Card(access_token=token,
             out_track_id=receive_out_track_id
             )

    # TODO 完成卡片字段值增删功能
    # update_card_vars = json.loads(previous_card.get(b"card_param_map_string").decode())
    update_card_item = json.loads(request.POST.get("value"))
    user_id = request.POST.get("userId")
    private_data = {user_id: {}}

    if "approve" in update_card_item["cardPrivateData"]["params"].keys():
        # 同意的私有变量
        if a.update_card_vars["approve"] < a.update_card_vars["approve_max"]:
            a.update_card_vars["approve"] += 1
        private_data = {user_id: {"approve_action": True}}
    else:
        # 否则为拒绝的私有变量
        if a.update_card_vars["reject"] < a.update_card_vars["reject_max"]:
            a.update_card_vars["reject"] += 1
        private_data = {user_id: {"reject_action": True}}

    # b = CardData(update_card_vars)
    # a.create_and_update_card_data(b)
    # a.send_interactive_card()

    # time.sleep(3)
    a.update_card_vars["markdown_content"] = a.update_card_vars["markdown_content"] + ". "
    b = CardData(a.update_card_vars)

    private_card_data = CardData(private_data[user_id])
    # logger.info(f"Card param map: {b.get_card_content()}")
    a.create_and_update_card_data(b)
    # a.__persistent_card()

    logger.info(f"开始更新卡片")
    a.update_interactive_card(user_id=user_id, private_data=private_card_data)
    return HttpResponse("OK")
