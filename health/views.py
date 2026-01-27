from django.http import HttpResponse
from django.shortcuts import render


def live(request):
    """Health live"""
    return HttpResponse("OK")