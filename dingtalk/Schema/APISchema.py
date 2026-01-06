from pydantic import BaseModel, HttpUrl, Json, Field


class NewNoticeSchema(BaseModel):
    markdown_title: str
    markdown_content: str
    card_ref_link: HttpUrl
    commit_sha: str
    repository: str
    project_id: int
    author: str
    branch: str
    environment: str
    chart_data: Json
    task_name: str
    cicd_status: str
    card_title: str
    card_template_id: str
    open_conversation_id: str
    autoLayout: bool = Field(alias="config.autoLayout", default=False)
    cicd_elapse: str

    class Config:
        # 允许通过别名或变量名赋值
        populate_by_default = True