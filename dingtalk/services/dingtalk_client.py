import time

from alibabacloud_dingtalk.card_1_0.models import (CreateAndDeliverRequestImGroupOpenDeliverModel,
                                                   CreateCardRequestImGroupOpenSpaceModelNotification,
                                                   CreateAndDeliverRequestImGroupOpenSpaceModel)
from darabonba.policy.retry import RetryOptions, RetryCondition
from django.conf import settings
from django.core.handlers.asgi import ASGIRequest
from django.http import HttpRequest
from httpx import RequestError
from urllib3.exceptions import ResponseError

from core.redis_client import redis_hgetall, redis_hget
from dingtalk.Models.CardRepository import CardRepository
from dingtalk.Models.dingtalk_card_struct import DingTalkCardData, UserIdTypeModel, SpaceTypeEnum
from dingtalk.Models.request_data_model import ReqDataModel
from dingtalk.interface.AbstractIM import AbstractIMClient
from alibabacloud_tea_openapi import models as open_api_models
from typing import Optional, Dict, NoReturn
from dingtalk.services.dingtalk_base import DingtalkBase
from alibabacloud_dingtalk.card_1_0 import models as dingtalkcard__1__0_models
from alibabacloud_dingtalk.card_1_0.client import Client as dingtalkcard_1_0Client
from alibabacloud_tea_util import models as util_models
import logging

from dingtalk.type.types import TeaType, T
from utils.markdown_template import render_git_log_to_md

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

        self.data: Optional[DingTalkCardData] = DingTalkCardData()
        self.data.robot_code = settings.DINGTALK_ROBOT_CODE

        self._card_template_id: Optional[str] = None
        self._alert_content: str = "Test message."

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
            self._robot_code = robot_code

        self.space_type = space_type
        self.callback_type = callback_type
        # self.out_track_id = out_track_id if out_track_id else self.gen_out_track_id()
        # self.open_space_id = self.gen_open_space_id()
        # 创建并投放卡片
        self.im_group_open_deliver_model = CreateAndDeliverRequestImGroupOpenDeliverModel()
        self.im_group_open_deliver_model.robot_code = self._robot_code

        self.common_headers = None
        self.task_name = task_name

    @property
    def out_track_id(self) -> str:
        """
        生成根据模板ID和当前时间戳的 out_track_id, 唯一标示卡片的外部编码
        """
        logger.debug("生成out_track_id")
        time_tag = int(time.time() * 1000)
        return f"{self._card_template_id}.{time_tag}"

    @property
    def open_space_id(self) -> str:
        r"""
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

    def __send_interactive_card_req(self, card_data: DingTalkCardData) -> Dict[str, TeaType]:
        """准备底层客户端"""
        ret = {}

        logger.debug("initial interactive card headers.")
        im_group_interactive_card_headers = dingtalkcard__1__0_models.CreateAndDeliverHeaders()
        im_group_interactive_card_headers.x_acs_dingtalk_access_token = self.access_token

        # Card Request
        logger.debug("initial interactive card request.")
        im_group_interactive_card_request = dingtalkcard__1__0_models.CreateAndDeliverRequest()
        im_group_interactive_card_request.card_template_id = self.data.card_template_id
        im_group_interactive_card_request.out_track_id = self.data.out_track_id
        im_group_interactive_card_request.callback_type = self.callback_type
        im_group_interactive_card_request.open_space_id = card_data.open_space_id
        im_group_interactive_card_request.user_id_type = UserIdTypeModel.userId
        im_group_interactive_card_request.card_data = self.card_data(self.data.card_parm_map.model_dump())

        # imGroupOpenSpaceModel
        logger.debug("initial interactive imGroupOpenSpaceModel.")
        im_group_interactive_open_space_model = CreateAndDeliverRequestImGroupOpenSpaceModel()
        # 支持卡片消息转发操作
        im_group_interactive_open_space_model.support_forward = True
        # TODO: 测试IM群组卡片通知内容
        im_group_interactive_open_space_model.notification = CreateCardRequestImGroupOpenSpaceModelNotification(
            # 新卡片通知的外部预览信息
            alert_content=self._alert_content,
            # 是否关闭推送通知
            notification_off=False
        )

        # imGroupOpenDeliverModel
        logger.debug("initial interactive imGroupOpenDeliverModel.")
        im_group_interactive_open_deliver_model = dingtalkcard__1__0_models.CreateAndDeliverRequestImGroupOpenDeliverModel()
        im_group_interactive_open_deliver_model.robot_code = self.data.robot_code

        # 组装 request 参数
        im_group_interactive_card_request.im_group_open_space_model = im_group_interactive_open_space_model
        im_group_interactive_card_request.im_group_open_deliver_model = im_group_interactive_open_deliver_model

        logger.debug("initial interactive req RuntimeOptions.")
        runtime = util_models.RuntimeOptions()
        runtime.keep_alive = True

        ret["im_group_interactive_card_headers"] = im_group_interactive_card_headers
        ret["im_group_interactive_card_request"] = im_group_interactive_card_request
        ret["im_group_interactive_open_space_model"] = im_group_interactive_open_space_model
        ret["im_group_interactive_open_deliver_model"] = im_group_interactive_open_deliver_model
        ret["runtime"] = runtime

        return ret

    def build_card_data(self, card_parm_map: T) -> DingTalkCardData:
        """装载 card parm data
        :param card_parm_map: 模型数据对象
        :return: DingTalkCardData: 返回模型数据对象
        """
        logger.debug(f"build card data. {card_parm_map}")
        card_data = DingTalkCardData(
            card_template_id=self.data.card_template_id,
            out_track_id=self.out_track_id,
            robot_code=self.data.robot_code,
            open_conversation_id=self.data.open_conversation_id,
            space_type=SpaceTypeEnum.IM_GROUP,
            task_name=self.task_name,
            card_parm_map=card_parm_map
        )
        return card_data

    # TODO: 完善持久化功能
    def __persistent_card(self) -> bool:
        """持久化卡片数据
        :param key: persistent key name
        :param timeout: 超时时间，默认值7day
        """
        return CardRepository.save(self.data)

        # mapping = DingTalkCardData()
        # mapping.card_template_id = self.card_template_id
        # mapping.conversation_type = self.conversation_type
        # mapping.robot_code = self._robot_code
        # mapping.open_conversation_id = self.open_conversation_id
        # mapping.task_name = self.task_name
        # mapping.card_parm_map = {"abc": "abc"}
        # mapping.private_data = {}
        # logger.info(f"persistent card key:{key}")
        # logger.debug(f"persistent card key:{key}, value:{mapping.model_json_schema()}")

    def __load_data_from_persistent_store(self, name: str, field: str = None) -> dict:
        """从历史数据中加载 card data
        :param name: persistent key name"""
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

    def parse_api_data(self, req_data: ReqDataModel) -> bool:
        """解析 API request 数据"""
        if req_data.method == 'POST':
            logger.info(f"request data parse ....")
            card_template_id = req_data.headers.get("x-card-template-id")
            self._card_template_id = card_template_id
            open_conversation_id = req_data.headers.get("x-open-conversation-id")
            task_name = req_data.POST.get("task_name")
            body = dict(req_data.POST)
            data = {"card_template_id": card_template_id,
                    "open_conversation_id": open_conversation_id,
                    "task_name": task_name,
                    "card_parm_map": body,
                    "robot_code": settings.DINGTALK_ROBOT_CODE,
                    "out_track_id": self.out_track_id
                    }
            schema = DingTalkCardData.model_validate(data)
            # render Markdown content
            schema.card_parm_map.markdown_content = render_git_log_to_md(schema.card_parm_map.markdown_content)
            logger.debug(f"parsed data {schema.model_dump()}")
            self.data = schema
            return True
        else:
            raise RequestError(message=f'request method {req_data.method} not supported')

    @staticmethod
    def card_data(card_param_map: dict[str, str]) -> dingtalkcard__1__0_models.CreateAndDeliverRequestCardData:
        """
        创建 card_data 对象.
        :param card_param_map: 卡片参数dict对象
        :return: CreateAndDeliverRequestCardData
        """
        request_card_data = dingtalkcard__1__0_models.CreateAndDeliverRequestCardData()
        request_card_data.card_param_map = card_param_map
        return request_card_data

    @property
    def im_client(self) -> dingtalkcard_1_0Client:
        logger.debug("initial IM client.")
        config = open_api_models.Config()
        config.protocol = "https"
        config.region_id = "central"
        retry_option = RetryOptions(
            options={"retryCondition": [RetryCondition(condition={"maxAttempts": 5})]}
        )
        config.retry_options = retry_option
        return dingtalkcard_1_0Client(config)

    def send(self) -> dingtalkcard__1__0_models.CreateAndDeliverResponse:
        """构造卡片对象和发送消息体"""
        req = self.__send_interactive_card_req(self.data)

        logger.info("sending card ....")
        resp: dingtalkcard__1__0_models.CreateAndDeliverResponse = self.im_client.create_and_deliver_with_options(
            request=req["im_group_interactive_card_request"],
            headers=req["im_group_interactive_card_headers"],
            runtime=req["runtime"],
        )
        self.__persistent_card()
        if resp.status_code == 200:
            return resp
        else:
            raise RuntimeError(resp)

    def update(self):
        """更新卡片"""
        pass

    def get_record_task_name_by_out_track_id(self, out_track_id):
        pass
