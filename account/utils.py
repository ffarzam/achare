import os

from django.core.validators import RegexValidator
from kavenegar import *
from rest_framework import exceptions

from achareh.custom_throttle import CustomScopedRateThrottle

PHONE_REGEX = r"^09\d{9}$"
phone_number_regex = RegexValidator(regex=PHONE_REGEX)

JTI_REGEX = r"^[0-9a-fA-F]{32}$"


def send_otp_with_sms(phone, code):
    try:
        API_KEY = os.environ.get("API_KEY")
        api = KavenegarAPI(API_KEY)

        params = {
            "receptor": f"{phone}",
            "template": "login",
            "token": f"{code}",
            "type": "sms",
        }
        response = api.verify_lookup(params)

        return code

    except APIException as e:
        return False

    except HTTPException as e:
        return False


def check_if_request_is_throttled(request, view, phone=None):
    throttle = CustomScopedRateThrottle(phone)
    throttle_durations = []
    if not throttle.allow_request(request, view):
        throttle_durations.append(throttle.wait())

    if throttle_durations:
        durations = [
            duration for duration in throttle_durations if duration is not None
        ]

        duration = max(durations, default=None)
        raise exceptions.Throttled(duration)


def add_request_to_throttle(request, view, phone=None):
    throttle = CustomScopedRateThrottle(phone)
    throttle.add_request(request, view)
