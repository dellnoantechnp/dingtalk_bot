from Tea.model import TeaModel
from django.http import HttpHeaders, QueryDict
from pydantic import BaseModel, Field
from typing_extensions import TypeVar

# 定义一个类型变量 T，且必须是 BaseModel 的子类
T = TypeVar("T", bound=BaseModel)

TeaType = TypeVar("TeaType", bound=TeaModel)
