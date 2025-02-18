import logging
from dingtalk.WatchJobStatus import gen_chart_data, get_task_job_from_workflows_api, settings
from typing import Union, Optional
from django_q.tasks import async_task, result, schedule
from django_q.models import Schedule, Task
from django.utils import timezone
from datetime import timedelta, datetime
from humanfriendly import format_timespan


def add_schedule_job(args,
                     minutes: float = 0.2,
                     repeat: int = -1) -> Schedule:
    """
    添加后台任务队列，默认 12s 执行一次
    :param args: worker 任务的入参，这里指的是 Workflows 任务的名称
    :param minutes: worker 任务的执行间隔， 默认 12s 执行一次
    :param repeat: worker 任务的重复周期，默认永久重复
    :return: 返回 Django_Q 的 Schedule 对象
    """
    logger = logging.getLogger("dingtalk_bot")
    logger.info(f"add schedule job {args}")
    task_id = schedule("dingtalk.tasks.TaskStatusOfWorkflowsJob.worker", args,
                       schedule_type=Schedule.MINUTES,
                       minutes=minutes,
                       repeats=repeat,
                       hook="dingtalk.tasks.TaskStatusOfWorkflowsJob.print_result")
    return task_id


def worker(task_name: Union[str] = "") -> list:
    """
    工作任务，根据 workflwos api 返回对象生成 chart_data 数据
    :param task_name: Workflows 任务的名称
    :return: chart data list
    """
    logger = logging.getLogger("dingtalk_bot")
    wf_api_result = get_task_job_from_workflows_api(token=settings.ARGO_WORKFLOWS_TOKEN,
                                                    api_domain=settings.ARGO_WORKFLOWS_DOMAIN,
                                                    namespace=settings.ARGO_WORKFLOWS_WORKER_NAMESPACE,
                                                    task_name=task_name
                                                    )
    if 400 <= wf_api_result.status_code <= 499:
        logger.warning(f"Get workflows api warning, workflows api status code [{wf_api_result.status_code}]"
                       f", remove this task.")
        remove_task(task_name=task_name)
        chart_data_result = ""
    elif 500 <= wf_api_result.status_code <= 599:
        logger.error(f"Get workflows api error status code [{wf_api_result.status_code}], retry to get task content.")
        chart_data_result = ""
    else:
        logger.info("Get workflows api content complete.")
        chart_data_result = gen_chart_data(wf_api_result)
        for item in chart_data_result:
            if item["x"] == "total" and item["y"] == 1.0:
                remove_task(task_name)
    return chart_data_result


def print_result(task):
    print("start print result.")
    print(repr(dir(task)))
    result = (f"id={task.id} "
              f"group_id={task.group} "
              f"args={task.args[0]} "
              f"name={task.name} "
              f"""duration="{format_timespan(task.stopped - task.started)}" """
              f"success={task.success} "
              f"task_result={task.result}")
    #result = "12345"

    print(f"{datetime.now()} worker result is:", result)


def remove_task(task_name):
    print(f"Removing task {task_name} .....")
    test_arg = str((task_name,))
    Schedule.objects.filter(args=test_arg).delete()
