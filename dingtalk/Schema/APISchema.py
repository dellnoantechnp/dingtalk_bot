from pydantic import BaseModel, Field

from dingtalk.services.dingtalk_card_struct import DingTalkCardParmData


class SchemaConfig(BaseModel):
    class Config:
        # 是否允许通过模型属性名称填充字段
        validate_by_name = True
        # 是否允许通过模型属性别名填充字段
        validate_by_alias = True

class APISchema(SchemaConfig):
    """Schema data"""
    card_template_id: str = Field(default=None, alias="x-card-template-id", description="卡片模板ID")
    open_conversation_id: str = Field(default=None, alias="x-open-conversation-id", description="卡片消息群聊ID")
    robot_code: str = Field(default=None, description="机器人应用code")
    task_name: str = Field(default=None, description="workflow task name")
    card_view_data: DingTalkCardParmData = Field(default_factory=DingTalkCardParmData, description="卡片view数据结构")
