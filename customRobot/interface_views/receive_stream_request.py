from dingtalk.Dingtalk_Base import Dingtalk_Base
from django.views.decorators.csrf import csrf_exempt
from dingtalk.Card import Card, CardData
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
    logger.debug(f"appKey: {os.environ.get('DINGTALK_CLIENT_ID')} appSecret: {os.environ.get('DINGTALK_CLIENT_SECRET')}")
    dd = Dingtalk_Base(os.environ.get("DINGTALK_CLIENT_ID"), os.environ.get("DINGTALK_CLIENT_SECRET"), logger_name)
    token = dd.get_access_token()
    logger.info("token: " + token)
    receive_out_track_id = request.POST.get("outTrackId")
    logger.info(f"request parma outTrackId: {receive_out_track_id}")

    redis_cache = caches["default"]
    redis_client = redis_cache.client.get_client()
    previous_card = redis_client.hgetall(receive_out_track_id)

    # logger.info(request.POST.get("TOPIC"))
    a = Card(access_token=token,
             card_template_id=previous_card.get(b"card_template_id").decode(),
             robot_code=previous_card.get(b"robot_code").decode(),
             open_conversation_id=previous_card.get(b"open_conversation_id").decode(),
             )

    # TODO 完成卡片字段值增删功能
    update_card_vars = json.loads(previous_card.get(b"card_param_map_string").decode())
    update_card_item = json.loads(request.POST.get("value"))
    update_card_vars["approve"] = update_card_vars["approve"] + 1
    # for i in update_card_item:
    #     if i == "cardPrivateData":
    #         for var in update_card_vars[i]:
    #             var["params"]



    b = CardData(update_card_vars)
    a.create_and_update_card_data(b)
    a.send_interactive_card()

    time.sleep(3)
    update_card_vars["markdown_content"] = update_card_vars["markdown_content"] + "7890"
    b = CardData(update_card_vars)
    #logger.info(f"Card param map: {b.get_card_content()}")
    a.create_and_update_card_data(b)
    #a.__persistent_card()

    logger.info(f"开始更新卡片")
    a.update_interactive_card()
    return HttpResponse("OK")