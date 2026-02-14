from django.http import HttpResponse
from django.shortcuts import render

from health.checks import check_live


def live(request):
    """Health live"""
    check_live()
    return HttpResponse("OK")