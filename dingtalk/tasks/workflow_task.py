import logging
import os
from typing import Dict

from celery import Celery, shared_task
from django.conf import settings
from django.core.handlers.asgi import ASGIRequest
from django.utils.duration import duration_string
from httpcore import Request

from dingtalk.Models.dingtalk_card_struct import SpaceTypeEnum
from dingtalk.Models.request_data_model import ReqDataModel
from dingtalk.services.argo_workflows_service import ArgoWorkflowsService
from dingtalk.services.dingtalk_client import DingTalkClient
from utils.markdown_template import parse_user_name_from_git_log

logger = logging.getLogger("dingtalk_bot")

# 设置环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

app = Celery("workflows")

# namespace='CELERY'作用是允许你在Django配置文件中对Celery进行配置
# 但所有Celery配置项必须以CELERY开头，防止冲突
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动从Django的已注册app中发现任务
app.autodiscover_tasks()


@app.task(
    # 指定哪些异常触发自动重试
    autoretry_for=(Exception,),
    # 重试时的指数退避策略
    retry_backoff=True,
    # 重试次数上限
    retry_kwargs={'max_retries': 10},
    # 在指数退避的基础上增加随机抖动，避免大量任务同时重试
    retry_jitter=True,
    # 设定重试的最大延迟时间
    retry_backoff_max=10,
)
def fetch_task_info(namespace: str, task: str) -> Dict[str, str]:
    logger.debug("fetch_task_info starting...")
    workflow_instance = ArgoWorkflowsService()
    task_info = workflow_instance.get_result(
        namespace=namespace,
        name=task
    )
    logger.info(task_info)
    return task_info.model_dump()


@app.task(
    # 指定哪些异常触发自动重试
    autoretry_for=(Exception,),
    # 重试时的指数退避策略
    retry_backoff=True,
    # 重试次数上限
    retry_kwargs={'max_retries': 10},
    # 在指数退避的基础上增加随机抖动，避免大量任务同时重试
    retry_jitter=True,
    # 设定重试的最大延迟时间
    retry_backoff_max=10,
)
def create_and_update_card(req_data_dict: Dict[str, str]) -> Dict[str, str]:
    logger.debug("create_and_update_card starting...")
    namespace = settings.ARGO_WORKFLOWS_WORKER_NAMESPACE
    req_data = ReqDataModel(**req_data_dict)

    task_name = req_data.POST.get("task_name", "")
    workflow_instance = ArgoWorkflowsService()
    task_data = workflow_instance.get_result(
        namespace=namespace,
        name=task_name
    )
    change_log = workflow_instance.get_output_parameter(
        namespace=namespace,
        name=task_name
    )
    req_data.POST["markdown_content"] = change_log.value
    environment = workflow_instance.get_output_parameter(
        namespace=namespace,
        name=task_name,
        template_name="change-log",
        output_parameter="CI_ENVIRONMENT_NAME"
    )
    req_data.POST["environment"] = environment.value

    task_duration = workflow_instance.duration(
        namespace=namespace,
        name=task_name
    )
    req_data.POST["cicd_elapse"] = task_duration

    notice = DingTalkClient(
        task_name=task_name,
        space_type=SpaceTypeEnum.IM_GROUP
    )
    notice.parse_api_data(req_data=req_data)

    users = parse_user_name_from_git_log(change_log.value)
    logger.debug("users: {}".format(users))
    for user in users:
        logger.info(notice.search_userid_by_name(name=user).body)

    # @notice.before_send
    # def update_alert_text():
    #     notice._alert_content = notice.data.card_parm_map.repository + " 更新"

    # notice._alert_content = notice.data.card_parm_map.repository



    # @notice.before_send([test1])
    resp = notice.send()

    logger.info(resp.body)
    return notice.data.card_parm_map.model_dump()
