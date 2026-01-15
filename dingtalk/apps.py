import os

import dingtalk_stream
import requests
from dingtalk_stream import AckMessage
import logging
import threading

logger = logging.getLogger("dingtalk_bot")


def run():
    while True:
        logger.info(f"initial dingtalk stream threads ...")
        client_id = os.environ.get("DINGTALK_CLIENT_ID")
        client_secret = os.environ.get("DINGTALK_CLIENT_SECRET")
        logger.debug(f"client_id: {client_id}, client_secret: {client_secret}")
        credential = dingtalk_stream.Credential(client_id=client_id, client_secret=client_secret)
        client = dingtalk_stream.DingTalkStreamClient(credential)
        # client.register_callback_handler(dingtalk_stream.chatbot.ChatbotMessage.TOPIC,
        # self.EchoMarkdownHandler(logger=logger))
        ## 注册回调事件的 TOPIC
        client.register_callback_handler(dingtalk_stream.chatbot.ChatbotHandler.TOPIC_CARD_CALLBACK,
                                         EchoMarkdownHandler())
        t = threading.Thread(target=client.start_forever, name="dingtalk-stream", daemon=True)
        logger.info(f"start {t.name} thread ...")
        t.start()
        t.join()


# class CustomRobotConfig(AppConfig):
#     """启动 STREAM 后台线程，并注册 STREAM 回调接口"""
#     default_auto_field = 'django.db.models.BigAutoField'
#     name = 'customRobot'
#
#     def ready(self):
#         # 如果设置有环境变量 DISABLE_STREAM=true 则不启动 Stream 后台线程
#         if os.environ.get("DISABLE_STREAM", "false").lower() == "true":
#             return
#         self.run_dingtalk_stream()
#
#     def run_dingtalk_stream(self):
#         logger.info(f"initial dingtalk stream threads ...")
#         client_id = os.environ.get("DINGTALK_CLIENT_ID")
#         client_secret = os.environ.get("DINGTALK_CLIENT_SECRET")
#         credential = dingtalk_stream.Credential(client_id=client_id, client_secret=client_secret)
#         client = dingtalk_stream.DingTalkStreamClient(credential)
#         # client.register_callback_handler(dingtalk_stream.chatbot.ChatbotMessage.TOPIC,
#         # self.EchoMarkdownHandler(logger=logger))
#         ## 注册回调事件的 TOPIC
#         client.register_callback_handler(dingtalk_stream.chatbot.ChatbotHandler.TOPIC_CARD_CALLBACK,
#                                          self.EchoMarkdownHandler())
#         t = threading.Thread(target=client.start_forever, name="dingtalk-stream", daemon=True)
#         logger.info(f"start {t.name} thread ...")
#         t.start()
#         # loop = asyncio.get_event_loop()
#         # result = loop.run_until_complete(client.start())
#         # loop.close()


class EchoMarkdownHandler(dingtalk_stream.ChatbotHandler):

    def __init__(self):
        super().__init__()

    async def process(self, callback: dingtalk_stream.CallbackMessage):
        """
        Docs: https://open.dingtalk.com/document/orgapp/event-callback-card  事件回调的content
        """
        incoming_message = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
        # print(incoming_message.extensions["content"])
        # text = 'echo received message:\n'
        # text += '\n'.join(['> 1. %s' % i for i in incoming_message.text.content.strip().split('\n')])
        # 回复一个 markdown 卡片消息
        # self.reply_markdown('dingtalk-tutorial-python', text, incoming_message)
        # 回复一个普通文本消息
        # self.reply_text(text=text, incoming_message=incoming_message)
        # return AckMessage.STATUS_OK, 'OK'
        # 获取STREAM回调数据
        post_data = incoming_message.to_dict()
        # 调用接口请求，处理卡片数据，更新卡片内容
        logger.debug(f"call back raw_data: {post_data}")
        try:
            resp = requests.post("http://localhost:8000/customRobot/test5", data=post_data)
            if resp.status_code >= 500:
                return AckMessage.STATUS_SYSTEM_EXCEPTION, "INTERNAL ERROR"
            elif resp.status_code == 400:
                return AckMessage.STATUS_BAD_REQUEST, "Bad Request"
            elif resp.status_code == 200:
                return AckMessage.STATUS_OK, 'OK'
        except Exception as e:
            raise Exception(f"Call back api response error, {e}")
