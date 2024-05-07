import dingtalk_stream
import logging
from dingtalk_stream import AckMessage


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
