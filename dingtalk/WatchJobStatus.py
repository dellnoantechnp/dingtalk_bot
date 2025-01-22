import json
import httpx
from dingtalk.HttpxCustomBearerAuth import CustomBearerAuth
from typing import Optional, Union
from django.conf import settings


def gen_chart_data(workflows_api_task_content):
    data = []
    children = []

    nodes = json.loads(workflows_api_task_content)["status"]["nodes"]

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
                                    task_name: Union[str]):
    auth = CustomBearerAuth(
        token=token)
    request = httpx.Client(auth=auth, timeout=30, http2=True)

    url = f"{api_domain}/api/v1/workflows/{namespace}/{task_name}"

    response = request.get(url=url)

    if response.status_code == httpx.codes.OK:
        return response.text
    else:
        raise Exception(f"Code: {response.status_code}, Argo-Workflows api request error. ")

#a = get_task_job_from_workflows_api(token=token, api_domain="https://workflows.poc.jagat.io", namespace="workflows", task_name="cicd-java-webhook-socket-server-92a4a10-47ftf")

#print(gen_chart_data(a))