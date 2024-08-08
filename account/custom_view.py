from abc import ABC

from rest_framework.views import APIView

from account.core.general import get_ip_from_request
from account.utils import check_if_request_is_throttled


class CustomAPIView(ABC, APIView):
    def initial(self, request, *args, **kwargs):
        ip = get_ip_from_request(request)

        if phone := request.data.get("phone", f"{ip}_NONE"):
            check_if_request_is_throttled(request, self, phone=phone)

        check_if_request_is_throttled(request, self)
        super().initial(request, *args, **kwargs)

    def get_serializer_context(self):
        return {"request": self.request, "format": self.format_kwarg, "view": self}
