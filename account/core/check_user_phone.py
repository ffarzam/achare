import math
import random
import time
from typing import Tuple

from django.conf import settings
from django.core.cache import caches

from account.core.general import get_ip_from_request
from account.utils import send_otp_with_sms


def save_otp_inside_cache(phone: str, code: str) -> None:
    caches["otp"].set(phone, code)


def get_phone_from_serializer(serializer) -> str:
    return serializer.validated_data.get("phone")


def generate_six_digit_code():
    digits = [i for i in range(0, 10)]
    random_str = ""
    for i in range(6):
        index = math.floor(random.random() * 10)
        random_str += str(digits[index])
    return random_str


def generate_otp_and_send(phone: str) -> Tuple[bool, str]:
    code = generate_six_digit_code()
    result = send_otp_with_sms(phone, code)
    return result, code


def save_history_of_ip_request(request) -> None:
    user_ip = get_ip_from_request(request)
    history = caches["throttle"].get(user_ip, [])
    history.insert(0, time.time())
    caches["throttle"].set(user_ip, history, settings.DURATION)


def get_history_of_ip_request(request) -> list:
    user_ip = get_ip_from_request(request)
    history = caches["throttle"].get(user_ip, [])
    return history


def wait(history):
    remaining_duration = settings.DURATION - (time.time() - history[0])
    return remaining_duration
