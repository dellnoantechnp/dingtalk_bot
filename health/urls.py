from django.urls import path, include, re_path

from health import views

urlpatterns = [
    path('ready', include("health_check.urls")),
    re_path(r'^live/?$', views.live, name='health-live')
]