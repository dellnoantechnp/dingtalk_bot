from enum import Enum
from typing import Any, Annotated, Dict

from django.http import HttpHeaders, QueryDict
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator


class HttpMethodEnum(str, Enum):
    """Http Method Enum"""
    POST = "POST"
    GET = "GET"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"
    DELETE = "DELETE"
    TRACE = "TRACE"
    PUT = "PUT"
    PATCH = "PATCH"


# 定义一个处理函数：将字典的所有 Key 转为小写
def to_lower_dict(v: Any) -> Dict[str, str]:
    if isinstance(v, dict):
        return {k.lower(): str(v) for k, v in v.items()}
    # 如果是 Django 的 HttpHeaders 或 QueryDict，先转 dict 再处理
    return {k.lower(): str(v) for k, v in dict(v).items()}

# 创建一个自定义类型
CaseInsensitiveDict = Annotated[Dict[str, str], BeforeValidator(to_lower_dict)]

class ReqDataModel(BaseModel):
    """Request Data Model"""
    #model_config = ConfigDict(arbitrary_types_allowed=True)

    method: HttpMethodEnum = Field(default=None, description="HttpRequest method string")
    headers: CaseInsensitiveDict | None = Field(default=None, description="HttpRequest headers data")
    GET: dict[str, str] | None = Field(default=None, description="HttpRequest get data")
    POST: dict[str, str] | None = Field(default=None, description="HttpRequest post data")
