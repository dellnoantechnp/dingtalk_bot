import json
import httpx
from dingtalk.HttpxCustomBearerAuth import CustomBearerAuth
from httpx._models import Response
from typing import Optional, Union
from django.conf import settings


def gen_chart_data(workflows_api_task_content: Response) -> list:
    """
    从 Workflows API 接口数据提取对应 chart_data 字段内容
    :param workflows_api_task_content: workflows API 接口返回内容
    :return: chart data list
    """
    data = []
    children = []

    nodes = workflows_api_task_content.json()["status"]["nodes"]

    # first filter
    for node in nodes:
        if nodes[node]["type"] == "TaskGroup":
            children = children + nodes[node]["children"]

    for node in nodes:
        if nodes[node]["type"] in ["Pod"]:
            status = nodes[node]["phase"]
            progress = nodes[node]["progress"].split('/')
            y_value = int(progress[0]) / int(progress[1])
            name = nodes[node]["displayName"]
            if node in children:
                pass
            else:
                data.append({"x": name, "y": y_value})

    # last filter
    for node in nodes:
        if nodes[node]["type"] == "DAG":
            progress = nodes[node]["progress"].split('/')
            y_value = int(progress[0]) / int(progress[1])
            data.append({"x": "total", "y": y_value})

    return data


def get_task_job_from_workflows_api(token: Union[str],
                                    api_domain: Union[str],
                                    namespace: Union[str],
                                    task_name: Union[str]) -> Response:
    """
    调用 Workflows API 接口，获取原始数据返回
    :param token: Workflows api token
    :param api_domain: Workflows api domain
    :param namespace: Workflows work task namespace
    :param task_name: Workflows 任务名称
    :return: api content response object
    """
    auth = CustomBearerAuth(token=token)
    request = httpx.Client(auth=auth, timeout=30, http2=True)

    url = f"{api_domain}/api/v1/workflows/{namespace}/{task_name}"

    response = request.get(url=url)

    return response

#a = get_task_job_from_workflows_api(token=token, api_domain="https://workflows.poc.jagat.io", namespace="workflows", task_name="cicd-java-webhook-socket-server-92a4a10-47ftf")

#print(gen_chart_data(a))