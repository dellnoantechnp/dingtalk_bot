"""
URL configuration for dingtalk_bot project.

The `urlpatterns` list routes URLs to interface_views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function interface_views
    1. Add an import:  from my_app import interface_views
    2. Add a URL to urlpatterns:  path('', interface_views.home, name='home')
Class-based interface_views
    1. Add an import:  from other_app.interface_views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('customRobot/', include("customRobot.urls")),
    path("health/", include("health_check.urls")),
    path('', include('django_prometheus.urls'))
]
