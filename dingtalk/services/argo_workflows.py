import json
from urllib.error import HTTPError

from argo_workflows.configuration import Configuration
from argo_workflows.api_client import ApiClient
from argo_workflows.api.workflow_service_api import WorkflowServiceApi
import httpx
from dingtalk.HttpxCustomBearerAuth import CustomBearerAuth
from httpx._models import Response
from typing import Optional, Union
from django.conf import settings

class ArgoWorkflowsService:
    def __init__(self):
        self._configuration = Configuration(host=settings.ARGO_WORKFLOWS_DOMAIN, access_token=settings.ARGO_WORKFLOWS_TOKEN)
        self._client = ApiClient(
            configuration=self._configuration,
            #header_name="Authorization",
            #header_value="Bearer " + settings.ARGO_WORKFLOWS_TOKEN
        )
        self.WorkflowServiceApi = WorkflowServiceApi(api_client=self._client)

    def get_result(self, namespace: str, name: str):
        a = self.WorkflowServiceApi.get_workflow(namespace=namespace, name=name)
        return a

if __name__ == "__main__":
    test = ArgoWorkflowsService()
    test.get_result(namespace="workflows", name="cicd-java-webhook-production-day99-fund-1aae7e7c-c9clg")


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
