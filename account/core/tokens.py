import datetime
from typing import Tuple
from uuid import uuid4

import jwt
from django.conf import settings
from django.core.cache import caches


def create_login_token(request, user) -> Tuple[str, str]:
    access_token, refresh_token, jti = generate_tokens(user)
    save_token_inside_cache(request, user, jti)
    return access_token, refresh_token


def generate_tokens(user) -> Tuple[str, ...]:
    jti = jti_maker()
    access_token = generate_access_token(user.id, jti)
    refresh_token = generate_refresh_token(user.id, jti)
    return access_token, refresh_token, jti


def jti_maker() -> str:
    return uuid4().hex


def generate_access_token(user_id: int, jti: str) -> str:
    access_token_payload = {
        "token_type": "access",
        "user_id": user_id,
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(seconds=settings.ACCESS_TOKEN_TTL),
        "iat": datetime.datetime.utcnow(),
        "jti": jti,
    }
    access_token = encode_jwt(access_token_payload)
    return access_token


def generate_refresh_token(user_id: int, jti: str) -> str:
    refresh_token_payload = {
        "token_type": "refresh",
        "user_id": user_id,
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(seconds=settings.REFRESH_TOKEN_TTL),
        "iat": datetime.datetime.utcnow(),
        "jti": jti,
    }
    refresh_token = encode_jwt(refresh_token_payload)
    return refresh_token


def generate_work_flow_token(phone: str) -> str:
    refresh_token_payload = {
        "token_type": "work_flow",
        "phone": phone,
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(seconds=settings.REDIS_WORK_FLOW_TTL),
        "iat": datetime.datetime.utcnow(),
    }
    refresh_token = encode_jwt(refresh_token_payload)
    return refresh_token


def decode_jwt(token: str) -> dict:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    return payload


def encode_jwt(payload: dict) -> str:
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


def cache_key_parser(arg: str):
    return arg.split(" || ")


def save_token_inside_cache(request, user, jti: str) -> None:
    key = cache_key_setter(user.id, jti)
    value = cache_value_setter(request)
    caches["auth"].set(key, value)


def cache_key_setter(user_id: int, jti: str) -> str:
    return f"user_{user_id} || {jti}"


def cache_value_setter(request) -> str:
    return request.META.get("HTTP_USER_AGENT", "UNKNOWN")


def create_work_flow_token(phone: str) -> str:
    work_flow_token = caches["work_flow"].set(phone)
    if not work_flow_token:
        work_flow_token = generate_work_flow_token(phone)
    return work_flow_token


def save_work_flow_token_in_cache(phone: str, token: str) -> None:
    caches["work_flow"].set(phone, token, settings.REDIS_WORK_FLOW_TTL)


def delete_all_sessions(user_id: int) -> None:
    caches["auth"].delete_many(caches["auth"].keys(f"user_{user_id} || *"))
