from django.urls import path
from . import views
import time


urlpatterns = [
    path('test', views.index),
    path("test2", views.dingtalk_stream1),
    path("test3", views.dingtalk_test),
    path("test4", views.interactive_card_test),
    path("test5", views.receive_stream_request)
]

