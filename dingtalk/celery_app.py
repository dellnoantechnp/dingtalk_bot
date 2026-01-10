import os

from celery import Celery

# 获取 settings.py 的配置信息
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dingtalk_bot.settings')

# 定义 Celery 对象，并将项目配置信息加载到对象中
# Celery 的参数一般以项目名称命名
celery_app = Celery('dingtalk')
celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()