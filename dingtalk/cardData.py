from alibabacloud_dingtalk.im_1_0.models import InteractiveCardCreateInstanceRequestCardData
import time


class CardData(InteractiveCardCreateInstanceRequestCardData):
    def __init__(self,
                 access_token: str = None,
                 card_template_id: str = None,
                 robot_code: str = None,
                 open_conversation_id: str = None,
                 conversation_type: int = 1,
                 open_space_id: str = None,
                 callback_type: str = "STREAM"
                 ):
        """初始化 Card 类相关的所有参数

        :param access_token: token
        :param card_template_id: 卡片模板ID
        :param robot_code: 机器人code
        :param open_conversation_id: 群ID
        :param conversation_type: 会话类型，0 单聊   1 群聊, 单聊不用填写open_conversation_id
        :param open_space_id: xxx
        :param callback_type: 回调模式， HTTP  STREAM
        """
        self.access_token = access_token
        self.card_tempalte_id = card_template_id
        self.robot_code = robot_code
        self.open_conversation_id = open_conversation_id
        self.conversation_type = conversation_type
        self.open_space_id = open_space_id
        self.callback_type = callback_type

    def gen_out_track_id(self) -> str:
        """生成根据模板ID和当前时间戳的 out_track_id, 唯一标示卡片的外部编码
        """
        time_tag = int(time.time() * 1000)
        return f"{self.card_template_id}.{time_tag}"
