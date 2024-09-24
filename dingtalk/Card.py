import logging

from alibabacloud_dingtalk.card_1_0.models import (CreateAndDeliverRequest, CreateAndDeliverHeaders,
                                                   CreateAndDeliverRequestImGroupOpenDeliverModel,
                                                   CreateCardRequestImGroupOpenSpaceModel,
                                                   CreateAndDeliverResponseBody)
from alibabacloud_dingtalk.im_1_0.models import (SendInteractiveCardRequest,
                                                 SendInteractiveCardHeaders)

from alibabacloud_dingtalk.card_1_0.models import (UpdateCardRequest,
                                                   UpdateCardHeaders,
                                                   UpdateCardResponseBody)
from alibabacloud_dingtalk.im_1_0.models import (UpdateInteractiveCardRequest,
                                                 UpdateInteractiveCardHeaders)

from alibabacloud_dingtalk.card_1_0.client import Client as dingtalkcard_1_0Client
from alibabacloud_dingtalk.im_1_0.client import Client as dingtalkim_1_0Client

# from alibabacloud_dingtalk.im_1_0 import models as dingtalkim__1__0_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from dingtalk.Dingtalk_Base import Dingtalk_Base
from django.core.cache import caches
import time
from typing import Optional, Union
from .CardData import CardData


class Card(CreateAndDeliverRequest, CreateAndDeliverHeaders, SendInteractiveCardRequest, SendInteractiveCardHeaders,
           UpdateCardRequest, UpdateCardHeaders, UpdateInteractiveCardHeaders, UpdateInteractiveCardRequest,
           open_api_models.Config, Dingtalk_Base):

    config = open_api_models.Config()
    config.protocol = "https"
    config.region_id = "central"

    def __init__(self, access_token: Union[str] = None,
                 card_template_id: Union[str] = None,
                 robot_code: Union[str] = None,
                 open_conversation_id: Union[str] = None,
                 conversation_type: Optional[int] = 1,
                 callback_type: Optional[str] = "STREAM",
                 out_track_id: Optional[str] = None):
        """初始化 Card 类相关的所有参数
        OpenSpaceId Docs: https://open.dingtalk.com/document/orgapp/open-interface-card-delivery-instance

        :param access_token: token
        :param card_template_id: 卡片模板ID
        :param robot_code: 机器人code
        :param open_conversation_id: 群ID
        :param conversation_type: 会话类型，0 单聊   1 群聊, 单聊不用填写open_conversation_id
        :#param open_space_id: 在投放接口中，使用openSpaceId作为统一投放id，openSpaceId采用固定协议且支持版本升级，主要由版本、场域类型、场域id三部分内容组成
        :param callback_type: 回调模式， HTTP  STREAM
        :param out_track_id: 回调请求时，需传入 out_track_id，新创建卡片不用传入 out_track_id
        """
        super().__init__(callback_type, card_template_id)
        super(CreateAndDeliverHeaders, self).__init__()
        self.logger = logging.getLogger("dingtalk_bot")
        self.x_acs_dingtalk_access_token = access_token
        self.card_template_id = card_template_id
        self.robot_code = robot_code
        self.open_conversation_id = open_conversation_id
        self.conversation_type = conversation_type
        self.callback_type = callback_type
        self.out_track_id = out_track_id if out_track_id else self.gen_out_track_id()
        self.open_space_id = self.gen_open_space_id()
        self.im_group_open_deliver_model = CreateAndDeliverRequestImGroupOpenDeliverModel()
        self.im_group_open_deliver_model.robot_code = self.robot_code
        self.im_group_open_space_model = CreateCardRequestImGroupOpenSpaceModel()
        self.im_group_open_space_model.support_forward = True
        self.common_headers = None

    def gen_out_track_id(self) -> str:
        """
        生成根据模板ID和当前时间戳的 out_track_id, 唯一标示卡片的外部编码
        """
        self.logger.debug("生成out_track_id")
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

    def create_and_update_card_data(self, card_data: CardData):
        """
        Create CardData object

        :param card_data: 卡片数据对象
        """
        self.logger.info(f"Card param map: {card_data.get_card_content()}")
        self.card_data = card_data

    def __deliver_card(self) -> CreateAndDeliverResponseBody:
        """
        生成和投递新的卡片
        """
        card_client = dingtalkcard_1_0Client(self.config)
        resp = card_client.create_and_deliver_with_options(
            self, self, util_models.RuntimeOptions()
        )
        return resp.body

    def __update_card(self) -> UpdateCardResponseBody:
        """
        更新卡片
        """
        self.card_update_options = None
        card_client = dingtalkcard_1_0Client(self.config)
        resp = card_client.update_card_with_options(
            self, self, util_models.RuntimeOptions()
        )
        return resp.body

    def send_interactive_card(self):
        """
        发送卡片到对应 IM 消息中
        """
        self.__deliver_card()
        im_client = dingtalkim_1_0Client(self.config)
        im_client.send_interactive_card_with_options(
            self, self, util_models.RuntimeOptions()
        )
        self.__persistent_card()

    def update_interactive_card(self):
        """
        更新卡片
        """

        update_card_response = self.__update_card()
        if update_card_response.success:
            self.logger.info(f"交互式卡片更新成功: {update_card_response.result}")
        else:
            self.logger.warning(f"交互式卡片更新失败: {update_card_response.result}")

        im_client = dingtalkim_1_0Client(self.config)
        im_client.update_interactive_card_with_options(
            self, self, util_models.RuntimeOptions()
        )

    def __persistent_card(self, timeout: Optional[int] = 604800):
        """
        持久化卡片数据
        """
        key_name = self.out_track_id
        mapping = dict()
        mapping["card_param_map_string"] = str(self.card_data)
        mapping["card_template_id"] = self.card_template_id
        mapping["out_track_id"] = self.out_track_id
        mapping["robot_code"] = self.robot_code
        mapping["open_conversation_id"] = self.open_conversation_id
        mapping["conversation_type"] = self.conversation_type
        self.logger.debug(f"persistent card data on out_track_id is {key_name}")

        redis_cache = caches["default"]
        redis_client = redis_cache.client.get_client()
        if redis_client.hset(name=key_name,
                             mapping=mapping):
            self.logger.debug(f"persistent card param {key_name} to redis done, ttl is {timeout}")
        redis_client.execute_command("expire", key_name, timeout)

    def __str__(self):
        print(repr(self))
