from datetime import datetime, timezone
from hera.workflows.models import NodeStatus
from hera.workflows import WorkflowsService
from typing import Dict, List
from django.conf import settings
import logging

from nice_duration import duration_string
from pyasn1.type.univ import Null

from dingtalk.Models.workflow_output_parameters_model import WorkflowOutputParameterModel
from dingtalk.Models.workflow_task_status_model import WorkflowTaskStatusModel

logger = logging.getLogger("dingtalk_bot")


class ArgoWorkflowsService:
    def __init__(self):
        self.service = WorkflowsService(
            host=settings.ARGO_WORKFLOWS_DOMAIN,
            verify_ssl=True,
            token=settings.ARGO_WORKFLOWS_TOKEN,
            namespace=settings.ARGO_WORKFLOWS_WORKER_NAMESPACE,
        )

    def get_result(self, namespace: str, name: str) -> WorkflowTaskStatusModel:
        """处理任务输出"""
        try:
            logger.debug(f"get workflow result: {namespace}/{name} ...")
            ret = self.service.get_workflow(namespace=namespace, name=name)

            status = ret.status.phase
            progress = ret.status.progress
            namespace = ret.metadata.namespace
            name = ret.metadata.name
            logger.debug(f"get workflow result: {namespace}/{name}, status={status}, progress={progress}")

            nodes = ret.status.nodes if ret.status.nodes else {}
            nodes_status = sorted([self.__node(nodes.get(node))
                                   for node in nodes
                                   if nodes.get(node).type == "Pod"], key=lambda x: x["started_at"])
            suspend = ret.spec.suspend
            total_task_count = len([id for id in ret.status.nodes if ret.status.nodes[id].type in ["Pod", "Skipped"]])
            complete_task_count = len([id for id in ret.status.nodes
                                       if ret.status.nodes[id].type == "Pod" and ret.status.nodes[id].phase == "Succeeded"])
            started_at = ret.status.started_at.__root__
            finished_at = ret.status.finished_at.__root__ if ret.status.finished_at else datetime.now(timezone.utc)

            # output parameters
            change_log = self.get_output_parameter(namespace=namespace, name=name,
                                                   template_name="change-log", output_parameter="CHANGE_LOG")
            environment = self.get_output_parameter(namespace=namespace, name=name,
                                      template_name="change-log", output_parameter="CI_ENVIRONMENT_NAME")
            if change_log.value and environment.value:
                output_parameter = [change_log, environment]
            else:
                output_parameter = Null

            wts = WorkflowTaskStatusModel.model_validate({
                "namespace": namespace,
                "name": name,
                "status": status,
                "suspend": suspend,
                # "progress": progress,
                "total_task_count": total_task_count,
                "complete_task_count": complete_task_count,
                "started_at": started_at,
                "finished_at": finished_at,
                "nodes": nodes_status,
                "outputs": output_parameter
            })
            return wts
        except Exception as e:
            raise Exception(f"Hera 获取 workflow 任务状态失败: {e}")

    @staticmethod
    def calculator_duration(node: NodeStatus) -> List[str|int]:
        """计算当前任务耗时，以可读方式输出"""
        start_at = node.started_at.__root__
        if not node.finished_at:
            logger.debug(f"node {node.name} is running ...")
            finished_at = datetime.now(timezone.utc)
        else:
            finished_at = node.finished_at.__root__
        return [duration_string(timedelta=(finished_at - start_at)), (finished_at - start_at).total_seconds()]

    def __node(self, node: NodeStatus) -> Dict[str, str]:
        """组装node字段"""
        ret = dict()
        ret["name"] = node.template_name
        ret["status"] = node.phase
        ret["duration"], ret["duration_time"]= self.calculator_duration(node)
        ret["started_at"] = node.started_at.__root__
        if node.phase != "Succeeded":
            ret["message"] = node.message
        return ret

    def get_output_parameter(self, namespace: str,
                   name: str, template_name: str = "change-log",
                   output_parameter: str = "CHANGE_LOG") -> WorkflowOutputParameterModel:
        logger.debug(f"get workflow result: {namespace}/{name} ...")
        ret = self.service.get_workflow(namespace=namespace, name=name)

        status = ret.status.phase
        progress = ret.status.progress
        logger.debug(f"get workflow result: {namespace}/{name}, status={status}, progress={progress}")

        workflow_output_data = WorkflowOutputParameterModel()

        if ret.status and ret.status.nodes:
            for node_id, node in ret.status.nodes.items():
                # 匹配指定任务模板名称
                if node.template_name == template_name:
                    # 获取输出参数列表
                    if node.outputs and node.outputs.parameters:
                        for item in node.outputs.parameters:
                            if item.name == output_parameter:
                                workflow_output_data.name = item.name
                                workflow_output_data.value = item.value
                                workflow_output_data.description = item.description
                                workflow_output_data.template_name = node.template_name
                                workflow_output_data.workflow_id = node.boundary_id
                                workflow_output_data.node_id = node_id
        return workflow_output_data

    def duration(self, namespace: str, name: str) -> str:
        """get workflow duration time string"""
        ret = self.service.get_workflow(namespace=namespace, name=name)
        started_at = ret.status.started_at.__root__
        status = ret.status.phase
        if status == "Running" and not ret.status.finished_at:
            finished_at = datetime.now(timezone.utc)
        else:
            finished_at = ret.status.finished_at.__root__
        duration = duration_string(timedelta=(finished_at - started_at))
        return duration



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
