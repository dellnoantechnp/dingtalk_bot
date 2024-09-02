from alibabacloud_dingtalk.card_1_0.models import (CreateAndDeliverRequest, CreateAndDeliverHeaders,
                                                   CreateAndDeliverRequestImGroupOpenDeliverModel,
                                                   CreateCardRequestImGroupOpenSpaceModel)
from alibabacloud_dingtalk.im_1_0.models import (InteractiveCardCreateInstanceRequestCardData,
                                                 SendInteractiveCardRequestCardData)
from alibabacloud_dingtalk.card_1_0.client import Client as dingtalkcard_1_0Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from dingtalk.Dingtalk_Base import Dingtalk_Base
import time
from .CardData import CardData


class Card(CreateAndDeliverRequest, CreateAndDeliverHeaders, open_api_models.Config, Dingtalk_Base):
    def __init__(self, access_token: str = None, card_template_id: str = None, robot_code: str = None,
                 open_conversation_id: str = None, conversation_type: int = 1,
                 callback_type: str = "STREAM"):
        """初始化 Card 类相关的所有参数
        OpenSpaceId Docs: https://open.dingtalk.com/document/orgapp/open-interface-card-delivery-instance

        :param access_token: token
        :param card_template_id: 卡片模板ID
        :param robot_code: 机器人code
        :param open_conversation_id: 群ID
        :param conversation_type: 会话类型，0 单聊   1 群聊, 单聊不用填写open_conversation_id
        :param open_space_id: 在投放接口中，使用openSpaceId作为统一投放id，openSpaceId采用固定协议且支持版本升级，主要由版本、场域类型、场域id三部分内容组成。
        :param callback_type: 回调模式， HTTP  STREAM
        """
        super().__init__(callback_type, card_template_id)
        super(CreateAndDeliverHeaders, self).__init__()
        self.x_acs_dingtalk_access_token = access_token
        self.card_template_id = card_template_id
        self.robot_code = robot_code
        self.open_conversation_id = open_conversation_id
        self.conversation_type = conversation_type
        self.callback_type = callback_type
        self.out_track_id = self.gen_out_track_id()
        self.open_space_id = self.gen_open_space_id()
        self.im_group_open_deliver_model = CreateAndDeliverRequestImGroupOpenDeliverModel()
        self.im_group_open_space_model = CreateCardRequestImGroupOpenSpaceModel()
        self.im_group_open_space_model.support_forward = True
        self.config = open_api_models.Config()
        self.config.protocol = "https"
        self.config.region_id = "central"

    def gen_out_track_id(self) -> str:
        """
        生成根据模板ID和当前时间戳的 out_track_id, 唯一标示卡片的外部编码
        """
        time_tag = int(time.time() * 1000)
        return f"{self.card_template_id}.{time_tag}"

    def gen_open_space_id(self) -> str:
        """
        在将卡片投放到不同的场域时，使用outTrackId唯一标识一张卡片，通过openSpaceId标识需要被投放的场域及其
        场域Id，通过openDeliverModels传入不同的投放场域。
        | 场域类型     | SpaceType      | SpaceId            | SpaceId 含义  |
        | ----------- | -------------- | ------------------ | ------------ |
        | IM群聊	      | IM_GROUP       | openConversationId | 会话id       |
        | IM单聊酷应用 | IM_SINGLE       | openConversationId | 会话id       |
        | IM机器人单聊 | IM_ROBOT	       | userId/unionId     | 员工id       |
        | 吊顶	     | ONE_BOX	       | openConversationId | 会话id       |
        | 协作	     | COOPERATON_FEED | userId/unionId     | 员工id       |
        | 文档	     | DOC	           | docKey             | 文档key      |
        :return: OpenSpaceId Str
        """
        if self.conversation_type == 1:
            return f"dtv1.card//IM_SINGLE.{self.open_conversation_id}"
        else:
            return "None"

    def create_card_data(self, card_data: CardData):
        self.card_data = card_data
        pass

    def deliver_card(self):
        self.config
        card_client = dingtalkcard_1_0Client(self.config)
        card_client.create_and_deliver_with_options(
            self, self, util_models.RuntimeOptions()
        )


    def send_card(self):
        pass

    def __str__(self):
        print(repr(self))