from enum import Enum
from typing import Generic
from pydantic import BaseModel, Field, HttpUrl, computed_field, model_validator
from typing_extensions import Annotated

from dingtalk.type.types import T


class DingTalkCardPrivateDataItem(BaseModel):
    """DingTalk interactive card private data"""
    approve_action: bool = False
    reject_action: bool = False


EntityUserID = Annotated[int, Field(gt=0, description="DingTalk UserID")]


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
    approve_max: str = Field(default="10", description="投票上限", ge=0, le=10)
    reject_max: str = Field(default="2", description="拒绝上限", ge=0, le=2)
    markdown_content: str = Field(default=None, description="消息内容markdown")
    approve: str = Field(default="0", description="当前投票数", ge=0, le=10)
    reject: str = Field(default="0", description="当前拒绝数", ge=0, le=2)
    card_title: str = Field(default=None, description="卡片通知标题")
    markdown_title: str = Field(default=None, description="消息体markdown的标题")
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





# class Enum:
#     name: Optional[str] = None
#
#     def __init__(self, value: int) -> None:
#         self.value = value
#
#     def __repr__(self) -> str:
#         return f"<{self.name}: {self.value}>"
#
#     def __str__(self) -> int:
#         return self.value
#
#
# class ConversationEnum(Enum):
#     name = "conversation_type"
#
# SINGLE_SESSION = ConversationEnum(value=0)
# GROUP_SESSION = ConversationEnum(value=1)


# class DingtalkCardData2(NamedTuple):
#     """DingTalk Card Data"""
#     task_name: str = None
#     card_parm_map_string: dict[int, str] = None
#     card_template_id: str = None
#     out_track_id: str = None
#     robot_code: str = None
#     open_conversation_id: str = None
#     conversation_type: int = None
#     private_data: dict[int, str] = None
#
