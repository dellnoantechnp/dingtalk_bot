from Tea.model import TeaModel
from pydantic import BaseModel
from typing_extensions import TypeVar

# 定义一个类型变量 T，且必须是 BaseModel 的子类
T = TypeVar("T", bound=BaseModel)

TeaType = TypeVar("TeaType", bound=TeaModel)