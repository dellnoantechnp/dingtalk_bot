from hera.workflows.models import NodeStatus
from humanfriendly import format_timespan
from hera.workflows import WorkflowsService

from typing import Optional, Union, Dict
from django.conf import settings


class ArgoWorkflowsService:
    def __init__(self):
        self.service = WorkflowsService(
            host=settings.ARGO_WORKFLOWS_DOMAIN,
            verify_ssl=True,
            token=settings.ARGO_WORKFLOWS_TOKEN,
            namespace=settings.ARGO_WORKFLOWS_WORKER_NAMESPACE,
        )

    def get_result(self, namespace: str, name: str) -> dict[str, str]:
        """处理任务输出"""
        try:
            ret = self.service.get_workflow(namespace=namespace, name=name)

            status = ret.status.phase
            progress = ret.status.progress

            nodes = ret.status.nodes if ret.status.nodes else {}
            nodes_status = sorted([self.__node(nodes.get(node))
                                   for node in nodes
                                   if nodes.get(node).type == "Pod"], key=lambda x: x["started_at"])
            return {
                "name": name,
                "status": status,
                "progress": progress,
                "nodes": nodes_status
            }
        except Exception as e:
            raise Exception(f"Hera 获取 workflow 任务状态失败: {e}")

    @staticmethod
    def calculator_duration(node: NodeStatus) -> str:
        """计算当前任务耗时，以可读方式输出"""
        start_at = node.started_at.__root__
        finished_at = node.finished_at.__root__
        return format_timespan(finished_at - start_at)

    def __node(self, node: NodeStatus) -> Dict[str, str]:
        """组装node字段"""
        ret = dict()
        ret["name"] = node.template_name
        ret["status"] = node.phase
        ret["duration"] = self.calculator_duration(node)
        ret["started_at"] = node.started_at.__root__
        if node.phase != "Succeeded":
            ret["message"] = node.message
        return ret



if __name__ == "__main__":
    test = ArgoWorkflowsService()
    test.get_result(namespace="argo-workflows", name="xxxxxxx")

# def gen_chart_data(workflows_api_task_content: Response) -> list:
#     """
#     从 Workflows API 接口数据提取对应 chart_data 字段内容
#     :param workflows_api_task_content: workflows API 接口返回内容
#     :return: chart data list
#     """
#     data = []
#     children = []
#
#     nodes = workflows_api_task_content.json()["status"]["nodes"]
#
#     # first filter
#     for node in nodes:
#         if nodes[node]["type"] == "TaskGroup":
#             children = children + nodes[node]["children"]
#
#     for node in nodes:
#         if nodes[node]["type"] in ["Pod"]:
#             status = nodes[node]["phase"]
#             progress = nodes[node]["progress"].split('/')
#             y_value = int(progress[0]) / int(progress[1])
#             name = nodes[node]["displayName"]
#             if node in children:
#                 pass
#             else:
#                 data.append({"x": name, "y": y_value})
#
#     # last filter
#     for node in nodes:
#         if nodes[node]["type"] == "DAG":
#             progress = nodes[node]["progress"].split('/')
#             y_value = int(progress[0]) / int(progress[1])
#             data.append({"x": "total", "y": y_value})
#
#     return data
#
#
# def get_task_job_from_workflows_api(token: Union[str],
#                                     api_domain: Union[str],
#                                     namespace: Union[str],
#                                     task_name: Union[str]) -> Response:
#     """
#     调用 Workflows API 接口，获取原始数据返回
#     :param token: Workflows api token
#     :param api_domain: Workflows api domain
#     :param namespace: Workflows work task namespace
#     :param task_name: Workflows 任务名称
#     :return: api content response object
#     """
#     auth = CustomBearerAuth(token=token)
#     request = httpx.Client(auth=auth, timeout=30, http2=True)
#
#     url = f"{api_domain}/api/v1/workflows/{namespace}/{task_name}"
#
#     try:
#         response = request.get(url=url)
#     except (httpx.ConnectError, httpx.ConnectTimeout) as e:
#         raise ConnectionError(f"Connection workflows api {api_domain} error: {e}")
#     except httpx.HTTPError as e:
#         raise HTTPError(f"HTTPError workflows api {api_domain} error: {e}")
#
#
#     return response
