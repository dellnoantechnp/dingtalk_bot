import logging

import Tea.exceptions
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
from dingtalk.CardException import (PersistentDataError,
                                    LoadPersistentDataError,
                                    SendCardRobotNotFoundException)
from django.core.cache import caches
from django.core.cache.backends.redis import RedisCacheClient
import time
from typing import Optional, Union
from dingtalk.CardData import CardData
import json
import copy


class Card(CreateAndDeliverRequest, CreateAndDeliverHeaders, SendInteractiveCardRequest, SendInteractiveCardHeaders,
           UpdateCardRequest, UpdateCardHeaders, UpdateInteractiveCardHeaders, UpdateInteractiveCardRequest,
           open_api_models.Config, Dingtalk_Base):
    config = open_api_models.Config()
    config.protocol = "https"
    config.region_id = "central"

    def __init__(self, access_token: Union[str] = None,
                 task_name: Optional[str] = "",
                 card_template_id: Optional[str] = None,
                 robot_code: Optional[str] = None,
                 open_conversation_id: Optional[str] = None,
                 conversation_type: Optional[int] = 1,
                 callback_type: Optional[str] = "STREAM",
                 out_track_id: Optional[str] = None):
        """初始化 Card 类相关的所有参数
        OpenSpaceId Docs: https://open.dingtalk.com/document/orgapp/open-interface-card-delivery-instance

        :param access_token: token
        :param task_name: 任务名称
        :param card_template_id: 卡片模板ID
        :param robot_code: 机器人code
        :param open_conversation_id: 群ID
        :param conversation_type: 会话类型，0 单聊   1 群聊, 单聊不用填写open_conversation_id
        :#param open_space_id: 在投放接口中，使用openSpaceId作为统一投放id，openSpaceId采用固定协议且支持版本升级，主要由版本、场域类型、场域id三部分内容组成
        :param callback_type: 回调模式， HTTP  STREAM
        :param out_track_id: 回调请求时，需传入 out_track_id，新创建卡片不用传入 out_track_id
        """
        self.logger = logging.getLogger("dingtalk_bot")
        super().__init__(callback_type, card_template_id)
        super(CreateAndDeliverHeaders, self).__init__()
        self.task_track_mapping_key_name = "cicd_task_name_mapping_out_track_id"
        if out_track_id and card_template_id is None:
            # 更新卡片逻辑,从历史数据中加载相关参数
            task_name = self.get_record_task_name_by_out_track_id(out_track_id=out_track_id)
            self.logger.info(f"load card parameters from redis, task_name={task_name}")
            self.__load_data_from_persistent_store(task_name=task_name)
        else:
            # 新创建卡片逻辑,需要传入初始参数
            self.logger.debug(
                f"create new card, card_template_id={card_template_id} robot_code={robot_code} open_conversation_id={open_conversation_id}")
            self.card_template_id = card_template_id
            self.robot_code = robot_code
            self.open_conversation_id = open_conversation_id

        self.x_acs_dingtalk_access_token = access_token
        self.conversation_type = conversation_type
        self.callback_type = callback_type
        self.out_track_id = out_track_id if out_track_id else self.gen_out_track_id()
        self.open_space_id = self.gen_open_space_id()
        self.im_group_open_deliver_model = CreateAndDeliverRequestImGroupOpenDeliverModel()
        self.im_group_open_deliver_model.robot_code = self.robot_code
        self.im_group_open_space_model = CreateCardRequestImGroupOpenSpaceModel()
        self.im_group_open_space_model.support_forward = True
        self.common_headers = None
        self.task_name = task_name

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
        # self.private_data = card_data

    def __deliver_card(self) -> CreateAndDeliverResponseBody:
        """
        生成和投递新的卡片
        """
        card_client = dingtalkcard_1_0Client(self.config)
        resp = card_client.create_and_deliver_with_options(
            self, self, util_models.RuntimeOptions()
        )
        return resp.body

    def __update_card(self, user_id: Optional[str] = None,
                      private_data: CardData = None) -> UpdateCardResponseBody:
        """
        更新卡片
        """
        self.card_update_options = None
        # if user_id and private_data:
        #    self.private_data = {user_id: private_data}
        card_client = dingtalkcard_1_0Client(self.config)
        resp = card_client.update_card_with_options(
            self, self, util_models.RuntimeOptions()
        )
        if user_id and private_data:
            self.private_data = {user_id: private_data}
        return resp.body

    def send_interactive_card(self):
        """
        新创建并发送卡片到对应 IM 消息中
        """
        self.__deliver_card()
        im_client = dingtalkim_1_0Client(self.config)
        try:
            im_client.send_interactive_card_with_options(
                self, self, util_models.RuntimeOptions()
            )
        except Tea.exceptions.TeaException as err:
            if err.statusCode == 400 and err.code == "chatbot.notFound":
                raise SendCardRobotNotFoundException(origin_message=err.message, status=err.statusCode)

        self.__persistent_card()
        self.set_record_task_name_by_out_track_id(out_track_id=self.out_track_id, task_name=self.task_name)

    def update_interactive_card(self, user_id: Optional[str] = None, private_data: Optional[CardData] = None):
        """
        更新卡片历史卡片
        """
        # if user_id and private_data:
        #     self.logger.debug(f"开始更新卡片私有变量内容: 用户ID {user_id}")
        #     update_card_response = self.__update_card(user_id=user_id, private_data=private_data)
        # else:
        #     self.logger.debug(f"开始更新卡片变量内容")
        #     update_card_response = self.__update_card()
        # if update_card_response.success:
        #     self.logger.info(f"交互式卡片更新成功: {update_card_response.result}")
        # else:
        #     self.logger.warning(f"交互式卡片更新失败: {update_card_response.result}")

        im_client = dingtalkim_1_0Client(self.config)

        # if private_data:
        #     self.private_data = json.dumps(private_data)

        im_client.update_interactive_card_with_options(
            self, self, util_models.RuntimeOptions()
        )
        self.__persistent_card()

    def __persistent_card(self, timeout: Optional[int] = 604800):
        """
        持久化卡片数据
        :param timeout: 可选的超时时间，默认值7day
        """
        # key_name = self.out_track_id
        key_name = self.task_name
        mapping = dict()
        mapping["card_param_map_string"] = str(self.card_data)
        mapping["card_template_id"] = self.card_template_id
        mapping["out_track_id"] = self.out_track_id
        mapping["robot_code"] = self.robot_code
        mapping["open_conversation_id"] = self.open_conversation_id
        mapping["conversation_type"] = self.conversation_type
        # mapping["card_param_map_string"] = self.card_param_map_string
        self.logger.debug(f"persistent card public data on task_name is {key_name}")

        # 持久化私有变量
        temp_private_data = {}
        if self.private_data:
            temp_private_data = json.loads(self.__load_data_from_persistent_store(self.task_name, "private_data"))
            for user in self.private_data:
                temp_private_data[user] = str(self.private_data.get(user))
        mapping["private_data"] = json.dumps(temp_private_data)
        mapping = Card.Clear_mapping_value_is_none(mapping)
        self.logger.debug(f"persistent card private data on task_name is {key_name}")

        # 写入新数据
        if self.__get_redis_client().hset(name=key_name,
                                          mapping=mapping) >= 0:
            # redis_client.hset ret 0: update exists item
            # redis_client.hset ret 1: update or create a key, add 1 item
            # redis_client.hset ret more than 1: update or create a key, add more item
            self.logger.debug(f"persistent card param {key_name} to redis done, ttl is {timeout}")
            self.redis_client.execute_command("expire", key_name, timeout)
        else:
            raise PersistentDataError(f"persistent card data [{key_name}] failed.", 10001)

    def __load_data_from_persistent_store(self, task_name: Union[str], key_name: Optional[str] = None):
        """
        卡片更新逻辑，从历史数据中 load 关键参数

        :param task_name: 回调请求时，需传入 task_name，新创建卡片不用传入 task_name
        :param key_name: 仅返回指定 key_name 的持久化数据
        """
        previous_card = self.__get_redis_client().hgetall(task_name)
        if previous_card:
            if key_name:
                return previous_card.get(key_name.encode()).decode()
            else:
                self.card_template_id = previous_card.get(b"card_template_id").decode()
                self.robot_code = previous_card.get(b"robot_code").decode()
                self.open_conversation_id = previous_card.get(b"open_conversation_id").decode()
                self.conversation_type = previous_card.get(b"conversation_type").decode()
                self.out_track_id = previous_card.get(b"out_track_id").decode()

                # public data
                self.update_card_vars = json.loads(previous_card.get(b"card_param_map_string").decode())
                # private data
                self.load_private_data = json.loads(previous_card.get(b"private_data").decode())
                # if self.load_private_data:
                #     for user in self.load_private_data:
                #         self.private_data = {user: PrivateCardData(json.loads(load_private_data.get(user)))}
                # pass
        else:
            raise LoadPersistentDataError(f"Load persistent data error, key name is [{task_name}]", 10001)

    def __get_redis_client(self) -> RedisCacheClient:
        """
        返回 redis_client

        :return: redis_client
        """
        if not hasattr(self, "redis_client"):
            redis_cache = caches["default"]
            redis_client = redis_cache.client.get_client()
            self.redis_client = redis_client
        return self.redis_client

    def set_record_task_name_by_out_track_id(self, out_track_id: Union[str] = None,
                                             task_name: Union[str] = None,
                                             timeout: Optional[int] = 604800):
        """
        记录 task_name 和 out_track_id 映射键，如需更改 key 名，需要设置 object.task_track_mapping_key_name 值。

        :param out_track_id: outTrackId
        :param task_name: 任务名称
        :param timeout: redis key TTL timeout
        :return: void
        """
        __temp_map = {out_track_id: task_name}
        if self.__get_redis_client().hset(name=self.task_track_mapping_key_name,
                                          mapping=__temp_map) >= 0:
            # redis_client.hset ret 0: update exists item
            # redis_client.hset ret 1: update or create a key, add 1 item
            # redis_client.hset ret more than 1: update or create a key, add more item
            self.logger.debug(f"store out_track_id mapping success.")
            self.redis_client.execute_command("expire", self.task_track_mapping_key_name, timeout)
        else:
            raise PersistentDataError(f"store {self.task_track_mapping_key_name} failed.", 10002)

    def get_record_task_name_by_out_track_id(self, out_track_id: Union[str] = None) -> (str, None):
        """
        返回根据 out_track_id 查询得到 task_name.

        :param out_track_id: outTrackId
        :return: 返回 task_name 名称
        """
        try:
            result = self.__get_redis_client().hget(self.task_track_mapping_key_name, key=out_track_id)
            if len(result) > 0:
                return result.decode()
        except Exception as err:
            self.logger.error(
                f"error get task_name failed from {out_track_id} of redis key {self.task_track_mapping_key_name}")
            return

    @staticmethod
    def Clear_mapping_value_is_none(input_dict: Union[dict]) -> dict:
        __temp_dict = copy.deepcopy(input_dict)
        for key in input_dict:
            if not input_dict.get(key):
                __temp_dict.pop(key)
        return __temp_dict


    def __str__(self):
        print(repr(self))
