import dingtalk_stream
import time


class MyEventHandler(dingtalk_stream.EventHandler):
    async def process(self, event: dingtalk_stream.EventMessage):
        self.logger.info(repr(event))
        if event.headers.event_type != 'chat_update_title':
            # ignore events not equals `chat_update_title`; 忽略`chat_update_title`之外的其他事件；
            # 该示例仅演示 chat_update_title 类型的事件订阅；
            return dingtalk_stream.AckMessage.STATUS_OK, 'OK'
        self.logger.info(
            'received event, delay=%sms, eventType=%s, eventId=%s, eventBornTime=%d, eventCorpId=%s, '
            'eventUnifiedAppId=%s, data=%s',
            int(time.time() * 1000) - event.headers.event_born_time,
            event.headers.event_type,
            event.headers.event_id,
            event.headers.event_born_time,
            event.headers.event_corp_id,
            event.headers.event_unified_app_id,
            event.data)
        # put your code here; 可以在这里添加你的业务代码，处理事件订阅的业务逻辑；
        self.logger.info(123)

        return dingtalk_stream.AckMessage.STATUS_OK, 'OK'