from django.urls import path
from . import views
from .interface_views import receive_stream_request
import time


urlpatterns = [
    path('test', views.index),
    path("test2", views.dingtalk_stream1),
    path("test3", views.dingtalk_test),
    path("test4", views.interactive_card_test),
    path("test5", receive_stream_request.receive_stream_request)
]

