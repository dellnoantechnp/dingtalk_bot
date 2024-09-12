import asyncio
import os

import requests
from django.apps import AppConfig
import dingtalk_stream
from dingtalk_stream import AckMessage
import logging
import threading


class CustomrobotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'customRobot'

    def ready(self):
        self.run_dingtalk_stream()


    def run_dingtalk_stream(self):
        threads = []
        client_id = os.environ.get("DINGTALK_CLIENT_ID")
        client_secret = os.environ.get("DINGTALK_CLIENT_SECRET")
        credential = dingtalk_stream.Credential(client_id=client_id, client_secret=client_secret)
        client = dingtalk_stream.DingTalkStreamClient(credential)
        logger = logging.getLogger("dingtalk_bot")
        logger.setLevel("DEBUG")
        #client.register_callback_handler(dingtalk_stream.chatbot.ChatbotMessage.TOPIC, self.EchoMarkdownHandler(logger=logger))
        ## 注册回调事件的 TOPIC
        client.register_callback_handler(dingtalk_stream.chatbot.ChatbotHandler.TOPIC_CARD_CALLBACK, self.EchoMarkdownHandler(logger=logger))
        t = threading.Thread(target=client.start_forever, name="dingtalk_stream")
        t.daemon = True
        threads.append(t)
        t.start()
        # loop = asyncio.get_event_loop()
        # result = loop.run_until_complete(client.start())
        # loop.close()

    class EchoMarkdownHandler(dingtalk_stream.ChatbotHandler):
        def __init__(self, logger: logging.Logger = None):
            super(dingtalk_stream.ChatbotHandler, self).__init__()
            if logger:
                self.logger = logger

        async def process(self, callback: dingtalk_stream.CallbackMessage):
            ## Docs: https://open.dingtalk.com/document/orgapp/event-callback-card  事件回调的content
            incoming_message = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
            print(incoming_message.extensions["content"])
            text = 'echo received message:\n'
            #text += '\n'.join(['> 1. %s' % i for i in incoming_message.text.content.strip().split('\n')])
            # 回复一个 markdown 卡片消息
            #self.reply_markdown('dingtalk-tutorial-python', text, incoming_message)
            # 回复一个普通文本消息
            #self.reply_text(text=text, incoming_message=incoming_message)
            #return AckMessage.STATUS_OK, 'OK'
            return AckMessage.STATUS_OK, 'OK'