import logging


class IgnoreHealthCheckFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        return not (
            "/health/live" in msg
            or
            "/health/ready" in msg
        )