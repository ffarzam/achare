from rest_framework.serializers import BaseSerializer

from account.core.general import get_ip_from_request
from account.utils import add_request_to_throttle


class IsValidMixin:
    def is_valid(self, raise_exception=False):
        request = self.context.get("request")
        view = self.context.get("view")
        phone = self.initial_data.get("phone")
        ip = get_ip_from_request(request)

        if phone:
            add_request_to_throttle(
                request,
                view,
                phone,
            )
        else:
            add_request_to_throttle(
                request,
                view,
                f"{ip}_NONE",
            )

        add_request_to_throttle(self.context.get("request"), self.context.get("view"))
        super().is_valid(raise_exception=raise_exception)
