from datetime import timedelta
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class DingTalkCardPrivateDataItem(BaseModel):
    """DingTalk interactive card private data"""
    approve_action: bool = False
    reject_action: bool = False


class DingTalkCardParmData(BaseModel):
    """Card param data"""
    cicd_elapse: str = Field(default=None, description="耗时")
    cicd_status: str = Field(default=None, description="任务状态")
    environment: str = Field(default=None, description="环境名称")
    commit_sha: str = Field(default=None, description="Git commit sha")
    branch: str = Field(default=None, description="Git branch")
    author: str = Field(default=None, description="CICD action author")
    project_id: int = Field(default=None, description="工程项目id")
    repository: str = Field(default=None, description="工程项目名称")
    card_ref_link: str = HttpUrl
    approve_max: int = Field(default=10, description="投票上限", ge=0, le=10)
    reject_max: int = Field(default=2, description="拒绝上限", ge=0, le=2)
    markdown_content: str = Field(default=None, description="消息内容markdown")
    approve: int = Field(default=0, description="当前投票数", ge=0, le=10)
    reject: int = Field(default=0, description="当前拒绝数", ge=0, le=2)
    card_title: str = Field(default=None, description="卡片通知标题")
    markdown_title: str = Field(default=None, description="消息体markdown的标题")
    chart_data: str = Field(default=None, description="图表JSON体")


class DingTalkCardData(BaseModel):
    """DingTalk interactive card data"""
    card_template_id: str = Field(default=None, description="互动卡片模板ID")
    out_track_id: str = Field(default=None, description="卡片消息out_track_id")
    robot_code: str = Field(default=None, description="机器人应用code")
    open_conversation_id: str = Field(default=None, description="群聊ID")
    conversation_type: int = Field(default=None, description="群聊类型", ge=0, le=1)
    task_name: str = Field(default=None, description="workflows task name")
    card_parm_map_string: DingTalkCardParmData
    private_data: dict[int, DingTalkCardPrivateDataItem] = Field(default=[], description="private data list")





class Enum:
    name: Optional[str] = None

    def __init__(self, value: int) -> None:
        self.value = value

    def __repr__(self) -> str:
        return f"<{self.name}: {self.value}>"

    def __str__(self) -> int:
        return self.value


class ConversationEnum(Enum):
    name = "conversation_type"

SINGLE_SESSION = ConversationEnum(value=0)
GROUP_SESSION = ConversationEnum(value=1)


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
