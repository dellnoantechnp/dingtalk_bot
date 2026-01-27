from django.core.management.base import BaseCommand
from dingtalk.services.dingtalk_stream_service import run


class Command(BaseCommand):
    help = "Run DingTalk Stream daemon"

    requires_migrations_checks = False
    requires_system_checks = []

    def handle(self, *args, **options):
        run()