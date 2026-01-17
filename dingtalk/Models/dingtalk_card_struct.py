import json
from enum import Enum
from typing import Generic, List, Mapping, Any, Optional, Union, Dict
from pydantic import BaseModel, Field, HttpUrl, computed_field, model_validator, field_serializer
import logging
from typing_extensions import Annotated

from dingtalk.type.types import T

logger = logging.getLogger("dingtalk_bot")


class DingTalkCardPrivateDataItem(BaseModel):
    """DingTalk interactive card private data"""
    approve_action: str = Field(default="false", description="var approve_action, must be str")
    reject_action: str = Field(default="false", description="var reject_action, must be str")


EntityUserID = Annotated[str, Field(description="DingTalk UserID, must be str")]


class DingTalkCardParmData(BaseModel):
    """Card view param data
    https://open.dingtalk.com/document/orgapp/instructions-for-filling-in-api-card-data#445386b2a8qss
    根据文档说明，所有字段均为字符串。
    """
    cicd_elapse: str = Field(default=None, description="任务耗时")
    cicd_status: str = Field(default=None, description="任务状态")
    environment: str = Field(default=None, description="环境名称")
    commit_sha: str = Field(default=None, description="Git commit sha")
    branch: str = Field(default=None, description="Git branch")
    author: str = Field(default=None, description="CICD action author")
    project_id: str = Field(default=None, description="工程项目id")
    repository: str = Field(default=None, description="工程项目名称")
    card_ref_link: str = HttpUrl
    approve_max: str = Field(default="10", description="投票上限, must be str")
    reject_max: str = Field(default="2", description="拒绝上限, must be str")
    markdown_content: str = Field(default=None, description="消息内容markdown")
    approve: str = Field(default="0", description="当前投票数, must be str")
    reject: str = Field(default="0", description="当前拒绝数, must be str")
    card_title: str = Field(default=None, description="卡片通知标题")
    chart_data: str = Field(default=None, description="图表JSON体")


class SpaceTypeEnum(str, Enum):
    """Space Type"""
    # IM 群聊
    IM_GROUP = 'IM_GROUP'
    # IM 单聊酷应用
    IM_SINGLE = 'IM_SINGLE'
    # IM 机器人单聊
    IM_ROBOT = 'IM_ROBOT'
    # 吊顶
    ONE_BOX = 'ONE_BOX'


class OpenSpaceIdModel(BaseModel):
    space_type: SpaceTypeEnum = Field(description="会话场域类型")
    open_conversation_id: str = Field(description="外部传入的群会话ID")

    @computed_field
    @property
    def open_space_id(self) -> str:
        """生成 open_space_id 的计算逻辑"""
        prefix = "dtv1.card//"
        if self.space_type == SpaceTypeEnum.IM_ROBOT:
            raise ValueError(f"DingTalk SpaceType error. not support value [{self.space_type.value}]")
        return f"{prefix}{self.space_type.value}.{self.open_conversation_id}"

    def __fetch_userId(self):
        # TODO: IM 机器人单聊场景，返回 userId/unionId
        pass


class UserIdTypeModel(int, Enum):
    userId = 1
    unionId = 2


class DingTalkCardData(BaseModel, Generic[T]):
    """DingTalk interactive card data"""
    card_template_id: str = Field(default=None, description="互动卡片模板ID")
    out_track_id: str = Field(default=None, description="卡片消息out_track_id")
    robot_code: str = Field(default=None, description="机器人应用code")
    open_conversation_id: str = Field(default=None, description="群聊ID")
    space_type: SpaceTypeEnum = Field(default=SpaceTypeEnum.IM_GROUP, description="场域类型")
    task_name: str = Field(default=None, description="workflows 任务名称")
    # open_space_id: str | None = Field(default=None, description="场域ID")
    card_parm_map: DingTalkCardParmData = Field(default_factory=DingTalkCardParmData, description="卡片view数据字段")
    private_data: dict[EntityUserID, DingTalkCardPrivateDataItem] = Field(
        default_factory=dict,
        description="private data object"
    )

    # 隐藏的缓存字段，exclude=True 表示该字段不导出至json对象中
    final_open_space_id: str | None = Field(default=None, exclude=True)

    @computed_field
    @property
    def open_space_id(self) -> str | None:
        # 直接返回校验阶段计算好的内部字段值，不要再次实例化 OpenSpaceIdModel
        return self.final_open_space_id

    @model_validator(mode='after')
    def compute_and_verify_space_id(self) -> 'DingTalkCardData':
        if self.space_type and self.open_conversation_id:
            # 1. 异常逻辑校验
            if self.space_type == SpaceTypeEnum.IM_ROBOT:
                raise ValueError(f"IM机器人类型 {self.space_type} 不支持生成 open_space_id")

            # 2. 复用 OpenSpaceIdModel 的计算逻辑并缓存至内部字段 final_open_space_id
            temp_model = OpenSpaceIdModel(
                space_type=self.space_type,
                open_conversation_id=self.open_conversation_id
            )
            self.final_open_space_id = temp_model.open_space_id
        return self


class DingTalkStreamDataValueModel(BaseModel):
    cardPrivateData: Dict[str, Any] = Field(default=None, description="回调数据字段")


class DingTalkStreamDataModel(BaseModel):
    corpId: str = Field(default=None, description="企业组织ID")
    spaceType: str = Field(default="im", description="场域类型")
    userIdType: int = Field(default=1, description="用户ID表示类型，1：UserID  2：UnionID")
    userId: str = Field(default=None, description="用户 ID")
    spaceId: str = Field(default=None, description="场域ID")
    outTrackId: str = Field(default=None, description="卡片ID")
    atUsers: List[str] = Field(default_factory=list, description="@用户ID列表")
    value: Union[DingTalkStreamDataValueModel, Dict[str, Any], str, None] = Field(default=None, description="回调数据值")

    # set
    @model_validator(mode='after')
    def parse_value_string(self) -> "DingTalkStreamDataModel":
        if isinstance(self.value, str):
            try:
                # 尝试解析json字符串
                parsed_json = json.loads(self.value)
                # 转化为子模型
                self.value = DingTalkStreamDataValueModel.model_validate(parsed_json)
            except (json.JSONDecodeError, ValueError):
                # 解析失败或不符合模型，存储原始字符串
                logger.warning(f"DingTalkStreamDataModel.parse_value_string error: {self.value}")
                pass
        return self

    # dump
    @field_serializer('value')
    def serialize_value(self, value: Any, _info) -> Optional[str]:
        if value is None:
            return None
        # 如果是模型或字典，导出时转为 JSON 字符串
        if isinstance(value, (BaseModel, dict)):
            # 如果是模型，先转为字典
            data = value.model_dump() if isinstance(value, BaseModel) else value
            return json.dumps(data, ensure_ascii=False)
        return value
