import asyncio

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
        client_id = ""
        client_secret = ""
        credential = dingtalk_stream.Credential(client_id=client_id, client_secret=client_secret)
        client = dingtalk_stream.DingTalkStreamClient(credential)
        client.register_callback_handler(dingtalk_stream.chatbot.ChatbotMessage.TOPIC, self.EchoMarkdownHandler())
        t = threading.Thread(target=client.start_forever, name="dingtalk_stream")
        t.daemon = True
        threads.append(t)
        t.start()
        loop = asyncio.get_event_loop()
        # result = loop.run_until_complete(client.start())
        # loop.close()

    class EchoMarkdownHandler(dingtalk_stream.ChatbotHandler):
        def __init__(self, logger: logging.Logger = None):
            super(dingtalk_stream.ChatbotHandler, self).__init__()
            if logger:
                self.logger = logger

        async def process(self, callback: dingtalk_stream.CallbackMessage):
            incoming_message = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
            text = 'echo received message:\n'
            text += '\n'.join(['> 1. %s' % i for i in incoming_message.text.content.strip().split('\n')])
            self.reply_markdown('dingtalk-tutorial-python', text, incoming_message)
            return AckMessage.STATUS_OK, 'OK'