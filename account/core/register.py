from typing import Tuple

from django.core.cache import caches

from account.core.tokens import create_work_flow_token, save_work_flow_token_in_cache
from account.models import User


def get_code_and_phone_from_serializer(serializer) -> Tuple[str, str]:
    user_input_code = serializer.validated_data["code"]
    user_input_phone = serializer.validated_data["phone"]
    return user_input_phone, user_input_code


def is_otp_code_correct(main_code: str, user_input_code: str) -> bool:
    return main_code == user_input_code


def create_user_and_set_work_flow_token(user_input_phone: str):
    User.objects.get_or_create(phone=user_input_phone)
    work_flow_token = create_work_flow_token(user_input_phone)
    save_work_flow_token_in_cache(user_input_phone, work_flow_token)
    delete_otp_code_from_cache(user_input_phone)
    return work_flow_token


def delete_otp_code_from_cache(phone: str) -> None:
    caches["otp"].delete(phone)


def get_main_code_from_cache(phone: str) -> str:
    return caches["otp"].get(phone)
