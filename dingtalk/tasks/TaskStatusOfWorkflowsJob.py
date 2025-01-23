import logging
from dingtalk.WatchJobStatus import gen_chart_data, get_task_job_from_workflows_api, settings
from typing import Union, Optional
from django_q.tasks import async_task, result, schedule
from django_q.models import Schedule, Task
from django.utils import timezone
from datetime import timedelta


def add_schedule_job(args):
    logger = logging.getLogger("dingtalk_bot")
    logger.info(f"add schedule job {args}")
    task_id = schedule("dingtalk.tasks.TaskStatusOfWorkflowsJob.worker", args,
                       schedule_type=Schedule.MINUTES,
                       minutes=0.2,
                       repeats=-1,
                       hook="dingtalk.tasks.TaskStatusOfWorkflowsJob.print_result")
    return task_id


def worker(task_name: Union[str] = "") -> list:
    task_info = get_task_job_from_workflows_api(token=settings.ARGO_WORKFLOWS_TOKEN,
                                                api_domain=settings.ARGO_WORKFLOWS_DOMAIN,
                                                namespace=settings.ARGO_WORKFLOWS_WORKER_NAMESPACE,
                                                task_name=task_name
                                                )
    chart_data_result = gen_chart_data(task_info)
    for item in chart_data_result:
        if item["x"] == "total" and item["y"] == 1.0:
            remove_task(task_name)
    return chart_data_result


def print_result(task):
    print(task.result)


def remove_task(task_name):
    print(123)
    test_arg = str((task_name,))
    Schedule.objects.filter(args=test_arg).delete()
