import time

from alibabacloud_dingtalk.card_1_0.models import (CreateAndDeliverRequestImGroupOpenDeliverModel,
                                                   CreateCardRequestImGroupOpenSpaceModelNotification,
                                                   CreateAndDeliverRequestImGroupOpenSpaceModel)
from darabonba.policy.retry import RetryOptions, RetryCondition
from urllib3.exceptions import ResponseError

from core.redis_client import redis_hgetall, redis_hget
from dingtalk.Schema.APISchema import NewNoticeSchema
from dingtalk.interface.AbstractIM import AbstractIMClient
from alibabacloud_tea_openapi import models as open_api_models
from typing import Optional, Union, Any
from dingtalk.services.dingtalk_base import DingtalkBase
from alibabacloud_dingtalk.card_1_0 import models as dingtalkcard__1__0_models
from alibabacloud_dingtalk.im_1_0 import models as dingtalkim__1__0_models
from alibabacloud_dingtalk.im_1_0.client import Client as dingtalkim_1_0Client
from alibabacloud_tea_util import models as util_models
import logging

from dingtalk.services.dingtalk_card_struct import DingTalkCardData, SpaceTypeEnum, UserIdTypeModel, T

logger = logging.getLogger("dingtalk_bot")


class DingTalkClient(AbstractIMClient, DingtalkBase):

    def __init__(self, task_name: Optional[str] = "", card_template_id: Optional[str] = None,
                 robot_code: Optional[str] = None, open_conversation_id: Optional[str] = None,
                 space_type: Optional[str] = SpaceTypeEnum.IM_GROUP, callback_type: Optional[str] = "STREAM",
                 out_track_id: Optional[str] = None):
        """
        初始化 Card 类相关的所有参数
        OpenSpaceId Docs: https://open.dingtalk.com/document/orgapp/open-interface-card-delivery-instance
        :param task_name: workflows 任务名称
        :param card_template_id: 钉钉开放平台互动卡片模板ID
        :param robot_code: 机器人code
        :param open_conversation_id: 群聊ID
        :param space_type: 会话类型，0 单聊   1 群聊, 单聊不用填写open_conversation_id
        :#param open_space_id: 在投放接口中，使用openSpaceId作为统一投放id，openSpaceId采用固定协议且支持版本升级，主要由版本、场域类型、场域id三部分内容组成
        :param callback_type: 回调模式， HTTP  STREAM
        :param out_track_id: 回调请求时，需传入 out_track_id，新创建卡片不用传入 out_track_id
        """
        super().__init__()
        self.task_track_mapping_key_name = "cicd_task_name_mapping_out_track_id"
        if out_track_id and card_template_id is None:
            # 更新卡片逻辑,从历史数据中加载相关参数
            task_name = self.get_record_task_name_by_out_track_id(out_track_id=out_track_id)
            logger.info(f"load card parameters from redis, task_name={task_name}")
            self.__load_data_from_persistent_store(name=task_name)
        else:
            # 新创建卡片逻辑,需要传入初始参数
            logger.debug(
                f"create new card, card_template_id={card_template_id} robot_code={robot_code} open_conversation_id={open_conversation_id}")
            self.card_template_id = card_template_id
            self.robot_code = robot_code
            self.open_conversation_id = open_conversation_id

        self.space_type = space_type
        self.callback_type = callback_type
        # self.out_track_id = out_track_id if out_track_id else self.gen_out_track_id()
        # self.open_space_id = self.gen_open_space_id()
        # 创建并投放卡片
        self.im_group_open_deliver_model = CreateAndDeliverRequestImGroupOpenDeliverModel()
        self.im_group_open_deliver_model.robot_code = self.robot_code

        self.common_headers = None
        self.task_name = task_name

    @property
    def out_track_id(self) -> str:
        """
        生成根据模板ID和当前时间戳的 out_track_id, 唯一标示卡片的外部编码
        """
        logger.debug("生成out_track_id")
        time_tag = int(time.time() * 1000)
        return f"{self.card_template_id}.{time_tag}"

    @property
    def open_space_id(self) -> str:
        """
        在将卡片投放到不同的场域时，使用outTrackId唯一标识一张卡片，通过openSpaceId标识需要被投放的场域及其
        场域Id，通过openDeliverModels传入不同的投放场域。
        例如： 为：
        dtv1.card//IM_GROUP.cidg2bR***JzmpFY=  为 IM 群聊的 openSpaceId
        ---------- -------- -----------------
        |          |        \_ cidg2bR***JzmpFY= 为群会话的 openConversationId
        |          \_ IM_GROUP为群聊标识SpaceType
        \_ 其中dtv1.card//为前缀固定值.

        | 场域类型     | SpaceType        | SpaceId            | SpaceId 含义 |
        | ------------ | ---------------- | ------------------ | ------------ |
        | IM群聊	   | IM_GROUP         | openConversationId | 会话id       |
        | IM单聊酷应用 | IM_SINGLE        | openConversationId | 会话id       |
        | IM机器人单聊 | IM_ROBOT	      | userId/unionId     | 员工id       |
        | 吊顶	       | ONE_BOX	      | openConversationId | 会话id       |
        | 协作	       | COOPERATION_FEED | userId/unionId     | 员工id       |
        | 文档	       | DOC	          | docKey             | 文档key      |
        :return: OpenSpaceId Str
        """
        if self.conversation_type == 1:
            return f"dtv1.card//IM_SINGLE.{self.open_conversation_id}"
        else:
            raise ValueError("dingtalk conversation_type value must be 1.")

    def __send_interactive_card_req(self, card_data: DingTalkCardData) -> dict[str, Any]:
        ret = {}

        logger.debug("initial interactive card headers.")
        im_group_interactive_card_headers = dingtalkim__1__0_models.CreateAndDeliverHeaders()
        im_group_interactive_card_headers.x_acs_dingtalk_access_token = self.access_token



        # Card Request
        logger.debug("initial interactive card request.")
        im_group_interactive_card_request = dingtalkcard__1__0_models.CreateAndDeliverRequest()
        im_group_interactive_card_request.card_template_id = self.card_template_id
        im_group_interactive_card_request.out_track_id = self.out_track_id
        im_group_interactive_card_request.callback_type = self.callback_type
        im_group_interactive_card_request.open_space_id = card_data.open_space_id
        im_group_interactive_card_request.user_id_type = UserIdTypeModel.userId

        # TODO: card data
        # imgroup_interactive_card_request.card_data =
        # imgroup_interactive_card_request.private_data =

        # imGroupOpenSpaceModel
        logger.debug("initial interactive imGroupOpenSpaceModel.")
        im_group_interactive_open_space_model = CreateAndDeliverRequestImGroupOpenSpaceModel()
        # 支持卡片消息转发操作
        im_group_interactive_open_space_model.support_forward = True
        # TODO: 测试IM群组卡片通知内容
        im_group_interactive_open_space_model.notification = CreateCardRequestImGroupOpenSpaceModelNotification(
            alert_content="test alert content",
            notification_off=False
        )

        # imGroupOpenDeliverModel
        logger.debug("initial interactive imGroupOpenDeliverModel.")
        im_group_interactive_open_deliver_model = dingtalkcard__1__0_models.CreateAndDeliverRequestImGroupOpenDeliverModel()
        im_group_interactive_open_deliver_model.robot_code = self.robot_code
        #send_interactive_card_request.open_conversation_id = self.open_conversation_id
        #send_interactive_card_request.conversation_type = self.conversation_type
        # send_interactive_card_request.conversation_type

        # 组装 request 参数
        im_group_interactive_card_request.im_group_open_space_model = im_group_interactive_open_space_model
        im_group_interactive_card_request.im_group_open_deliver_model = im_group_interactive_open_deliver_model

        logger.debug("initial interactive req RuntimeOptions.")
        runtime = util_models.RuntimeOptions()
        runtime.keep_alive = True

        ret["im_group_interactive_card_headers"] = im_group_interactive_card_headers
        ret["im_group_interactive_card_request"] = im_group_interactive_card_request
        ret["runtime"] = runtime

        return ret

    def build_card_data(self, card_parm_map: T) -> DingTalkCardData[T]:
        logger.debug(f"build card data. {card_parm_map}")
        card_data = DingTalkCardData(
            card_template_id=self.card_template_id,
            out_track_id=self.out_track_id,
            robot_code=self.robot_code,
            open_conversation_id=self.open_conversation_id,
            space_type=SpaceTypeEnum.IM_GROUP,
            task_name=self.task_name,
            card_parm_map=card_parm_map
        )
        return card_data

    def __persistent_card(self, key: str, timeout: Optional[int] = 604800) -> bool:
        """持久化卡片数据
        :param key: persistent key name
        :param timeout: 超时时间，默认值7day
        """
        mapping = DingTalkCardData()
        mapping.card_template_id = self.card_template_id
        mapping.conversation_type = self.conversation_type
        mapping.robot_code = self.robot_code
        mapping.open_conversation_id = self.open_conversation_id
        mapping.task_name = self.task_name
        mapping.card_parm_map = {"abc": "abc"}
        mapping.private_data = {}
        logger.info(f"persistent card key:{key}")
        logger.debug(f"persistent card key:{key}, value:{mapping.model_json_schema()}")



    def __load_data_from_persistent_store(self, name: str, field: str = None) -> dict:
        if field:
            ret = redis_hget(key=self.task_track_mapping_key_name, field=field)
            if ret.ok:
                return ret.value
            else:
                raise ValueError(f"dingtalk get task_track_mapping_key {ret.key}.{ret.field} value error, {ret.reason}")
        else:
            ret = redis_hgetall(key=self.task_track_mapping_key_name)
            if ret.ok:
                return ret.value
            else:
                raise ValueError(f"dingtalk get task_track_mapping_key {ret.key} value error, {ret.reason}")

    @staticmethod
    def card_data(card_param_map: dict[str, str],
                  card_media_id_param_map=None
                  ) -> dingtalkcard__1__0_models.CreateAndDeliverRequestCardData:
        """
        创建 card_data 对象.
        :param card_param_map: 卡片参数dict对象
        :param card_media_id_param_map: 卡片多媒体对象dict
        """
        if card_media_id_param_map is None:
            card_media_id_param_map = {}
        request_card_data = dingtalkcard__1__0_models.CreateAndDeliverRequestCardData()
        request_card_data.card_param_map = card_param_map
        #card_data.media_id_param_map = card_media_id_param_map
        return request_card_data

    @property
    def im_client(self) -> dingtalkim_1_0Client:
        logger.debug("initial IM client.")
        config = open_api_models.Config()
        config.protocol = "https"
        config.region_id = "central"
        retry_option = RetryOptions(
            options={"retryCondition": RetryCondition(condition={"maxAttempts": 5})}
        )
        config.retry_options = retry_option
        return dingtalkim_1_0Client(config)

    # TODO: coding card param mapping...
    def data(self):
        pass

    def send(self) -> None:
        req = self.__send_interactive_card_req(self.card_param_map)

        logger.info("initial card data.")
        # TODO: coding there....
        # card_data = self.card_data(card_param_map=self.card_param_map,
        #                            card_media_id_param_map=self.card_media_id_param_map)
        req["send_interactive_card_request"].card_data = card_data

        resp: dingtalkim__1__0_models.SendInteractiveCardResponse = self.im_client.send_interactive_card_with_options(
            request=req["send_interactive_card_request"],
            headers=req["send_interactive_card_headers"],
            runtime=req["runtime"],
        )
        if resp.status_code == 200:
            return resp.body
        else:
            raise ResponseError(resp)

    def update(self):
        pass
