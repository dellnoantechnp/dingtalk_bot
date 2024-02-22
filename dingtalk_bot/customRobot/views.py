from django.shortcuts import render
from django.http.response import JsonResponse


def index(request):
    return JsonResponse({"foo": "bar"})