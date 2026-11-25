"""Control the publish dependency in one disposable browser run."""

from unittest.mock import patch

from redis.exceptions import ConnectionError

from tests.team.browser_safety import run_dir_from_environment


class NotificationPublishFault:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        marker = run_dir_from_environment() / "notification-publish-fault"
        if request.method == "POST" and request.path.endswith("/decision/") and marker.exists():
            marker.unlink()
            with patch("leave.events.Redis.from_url", side_effect=ConnectionError("SQE controlled Redis outage")):
                return self.get_response(request)
        return self.get_response(request)
