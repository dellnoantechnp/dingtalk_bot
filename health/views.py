from django.http import HttpResponse

from health.checks import check_live


def live(request):
    """Health live"""
    check_live()
    return HttpResponse("OK")