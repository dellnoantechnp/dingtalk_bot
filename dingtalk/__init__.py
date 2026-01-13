from dingtalk.celery_app import celery_app
from dingtalk.tasks.workflow_task import app as workflow_task
__all__ = ['celery_app', 'workflow_task']