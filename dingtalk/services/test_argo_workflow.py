import unittest
import pytest
from unittest.mock import patch, MagicMock
from hera.workflows.models import Workflow
from dingtalk.services.argo_workflows_service import ArgoWorkflowsService


def test_argo_get_result_logic():
    # 1. 准备 Mock 数据
    # 建议从 Argo 真实环境复制一份 JSON 存为文件，这里演示手动构造
    with open("mock/mock_workflow_data.json", "r") as f:
        import json
        mock_json = json.load(f)

    # 将 JSON 转换为 Hera 的 Workflow 对象
    mock_workflow_obj = Workflow.model_validate(mock_json)

    # 2. 使用 patch 拦截具体的实例方法
    # 需要 Mock 的原始代码包路径：'hera.workflows.service.WorkflowsService.get_workflow'
    # 这样当你的 ArgoWorkflowsService 调用 self.service.get_workflow 时，会被拦截
    with patch('hera.workflows.service.WorkflowsService.get_workflow') as mock_method:
        # 设置 Mock 方法的返回值为我们准备好的对象
        mock_method.return_value = mock_workflow_obj

        # 3. 执行业务代码
        service = ArgoWorkflowsService()
        result = service.get_result("test-ns", "test-name")

        # 4. 验证逻辑
        print(f"解析后的状态: {result.status}")
        assert result.namespace == "test-ns"
        assert len(result.nodes) > 0

# class MyTestCase(unittest.TestCase):
#     def test_something(self):
#         self.assertEqual(True, False)  # add assertion here
#
#
# if __name__ == '__main__':
#     unittest.main()
