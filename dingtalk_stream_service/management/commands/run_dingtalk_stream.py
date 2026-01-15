from django.core.management.base import BaseCommand
from dingtalk.apps import run


class Command(BaseCommand):
    help = "Run DingTalk Stream daemon"

    def handle(self, *args, **options):
        run()