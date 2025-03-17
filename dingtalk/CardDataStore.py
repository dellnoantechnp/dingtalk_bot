from django.core.cache import caches
from typing import Optional, Any, Dict


class CardDataStore:
    """Redis 存储类，用于管理任务相关的数据存储"""
    
    # 定义可用的字段名称
    VALID_FIELDS = {
        'access_token': '钉钉访问令牌',
        'task_name': '任务名称',
        'card_template_id': '卡片模板ID',
        'robot_code': '机器人code',
        'open_conversation_id': 'IM群ID',
        'out_track_id': '消息跟踪ID',
        'callback_type': '回调模式'  # 可选值: HTTP, STREAM
    }

    def __init__(self):
        """初始化 Redis 存储类"""
        _redis_cache = caches["default"]
        self.cache = _redis_cache.client.get_client()
        self.task_track_mapping_key = "cicd_task_name_mapping_out_track_id"

    def set_field(self, task_name: str, field: str, value: Any) -> bool:
        """设置指定任务的字段值
        
        Args:
            task_name: 任务名称，用作 Redis hash key
            field: 字段名称，必须是预定义的有效字段
            value: 要设置的值
        Returns:
            bool: 是否设置成功
        """
        if field not in self.VALID_FIELDS:
            raise ValueError(f"无效的字段名称: {field}，有效字段为: {list(self.VALID_FIELDS.keys())}")
        
        try:
            self.cache.hset(task_name, field, str(value))
            return True
        except Exception as e:
            print(f"设置字段值失败: {e}")
            return False

    def get_field(self, task_name: str, field: str) -> Optional[str]:
        """获取指定任务的字段值
        
        Args:
            task_name: 任务名称，用作 Redis hash key
            field: 字段名称，必须是预定义的有效字段
        Returns:
            Optional[str]: 字段值，如果不存在返回 None
        """
        if field not in self.VALID_FIELDS:
            raise ValueError(f"无效的字段名称: {field}，有效字段为: {list(self.VALID_FIELDS.keys())}")
        
        try:
            return self.cache.hget(task_name, field)
        except Exception as e:
            print(f"获取字段值失败: {e}")
            return None

    # 为每个字段提供专门的 get 和 set 方法
    def get_access_token(self, task_name: str) -> Optional[str]:
        """获取访问令牌"""
        return self.get_field(task_name, 'access_token')

    def set_access_token(self, task_name: str, value: str) -> bool:
        """设置访问令牌"""
        return self.set_field(task_name, 'access_token', value)

    def get_task_name(self, task_name: str) -> Optional[str]:
        """获取任务名称"""
        return self.get_field(task_name, 'task_name')

    def set_task_name(self, task_name: str, value: str) -> bool:
        """设置任务名称"""
        return self.set_field(task_name, 'task_name', value)

    def get_card_template_id(self, task_name: str) -> Optional[str]:
        """获取卡片模板ID"""
        return self.get_field(task_name, 'card_template_id')

    def set_card_template_id(self, task_name: str, value: str) -> bool:
        """设置卡片模板ID"""
        return self.set_field(task_name, 'card_template_id', value)

    def get_robot_code(self, task_name: str) -> Optional[str]:
        """获取机器人code"""
        return self.get_field(task_name, 'robot_code')

    def set_robot_code(self, task_name: str, value: str) -> bool:
        """设置机器人code"""
        return self.set_field(task_name, 'robot_code', value)

    def get_open_conversation_id(self, task_name: str) -> Optional[str]:
        """获取IM群ID"""
        return self.get_field(task_name, 'open_conversation_id')

    def set_open_conversation_id(self, task_name: str, value: str) -> bool:
        """设置IM群ID"""
        return self.set_field(task_name, 'open_conversation_id', value)

    def get_out_track_id(self, task_name: str) -> Optional[str]:
        """获取消息跟踪ID"""
        return self.get_field(task_name, 'out_track_id')

    def set_out_track_id(self, task_name: str, value: str) -> bool:
        """设置消息跟踪ID"""
        return self.set_field(task_name, 'out_track_id', value)

    def get_callback_type(self, task_name: str) -> Optional[str]:
        """获取回调模式"""
        return self.get_field(task_name, 'callback_type')

    def set_callback_type(self, task_name: str, value: str) -> bool:
        """设置回调模式"""
        if value not in ['HTTP', 'STREAM']:
            raise ValueError("callback_type 必须是 'HTTP' 或 'STREAM'")
        return self.set_field(task_name, 'callback_type', value)

    def get_conversation_type(self, task_name: str, value: int):
        """返回 open_conversation_type 字段值"""
        return self.get_field(task_name, "conversation_type")

    def set_conversation_type(self, task_name: str, value: int) -> bool:
        """设置 conversation_type"""
        return self.set_field(task_name, "conversation_type")

    def get_all_fields(self, task_name: str) -> Dict[str, str]:
        """获取指定任务的所有字段值
        
        Args:
            task_name: 任务名称
        Returns:
            Dict[str, str]: 所有字段及其值的字典
        """
        try:
            return self.cache.hgetall(task_name)
        except Exception as e:
            print(f"获取所有字段值失败: {e}")
            return {}
