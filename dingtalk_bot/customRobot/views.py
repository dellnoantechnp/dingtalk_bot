import alibabacloud_dingtalk.im_1_0.models
from django.shortcuts import render
from django.http.response import JsonResponse, HttpResponse
import dingtalk_stream
from . import EchoMarkdownHandler
import customRobot.dingtalk.Dingtalk_Base
from django.views.decorators.csrf import csrf_exempt
import logging


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

@csrf_exempt
def dingtalk_test(request):
    logger = setup_logger()
    logger.info(request.POST.get("appKey") + " " + request.POST.get("appSecret"))
    dd = customRobot.dingtalk.Dingtalk_Base.Dingtalk_Base(request.POST.get("appKey"), request.POST.get("appSecret"))
    return HttpResponse(dd.getAccessToken())

    alibabacloud_dingtalk.im_1_0.models.InteractiveCardCreateInstanceRequest