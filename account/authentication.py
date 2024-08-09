from abc import ABC

import jwt
from django.contrib.auth.backends import ModelBackend
from django.core.cache import caches
from rest_framework.authentication import TokenAuthentication

from account.core.tokens import decode_jwt
from account.enums.fault_code import FaultCode
from account.enums.user_state import UserSituation
from account.models import User
from achareh import custom_exception


class AbstractTokenAuthentication(ABC, TokenAuthentication):

    @staticmethod
    def get_payload(token):
        payload = decode_jwt(token)
        return payload

    @staticmethod
    def get_user_from_payload(payload):
        user_id = payload.get("user_id")
        try:
            user = User.objects.get(id=user_id)
        except:
            return None
        return user

    @staticmethod
    def validate_jti_token(payload):
        jti = payload.get("jti")
        user_id = payload.get("user_id")
        if not caches["auth"].keys(f"user_{user_id} || {jti}"):
            return None
        return True


class AccessTokenAuthentication(AbstractTokenAuthentication):

    def authenticate_credentials(self, access_token):
        try:
            payload = self.get_payload(access_token)
        except jwt.ExpiredSignatureError:
            raise custom_exception.ExpiredAccessTokenError

        if not self.validate_jti_token(payload):
            return None, None

        user = self.get_user_from_payload(payload)

        return user, payload


class RefreshTokenAuthentication(AbstractTokenAuthentication):
    def authenticate_credentials(self, refresh_token):
        try:
            payload = self.get_payload(refresh_token)
        except jwt.ExpiredSignatureError:
            raise custom_exception.ExpiredRefreshTokenError

        if not self.validate_jti_token(payload):
            return None, None

        user = self.get_user_from_payload(payload)

        return user, payload


class WorkFlowTokenAuthentication(AbstractTokenAuthentication):
    def authenticate_credentials(self, work_flow_token):
        try:
            payload = self.get_payload(work_flow_token)
        except jwt.ExpiredSignatureError:
            raise custom_exception.ExpiredWorkFlowTokenError

        if not self.validate_jti_token(payload):
            return None, None
        user = self.get_user_from_payload(payload)

        return user, payload

    @staticmethod
    def validate_jti_token(payload):
        phone = payload.get("phone")
        payload_jti = payload.get("jti")
        cache_jti = caches["work_flow"].get(phone)
        if cache_jti != payload_jti:
            return None
        return True


class PhoneAuthBackend(ModelBackend):
    def authenticate(self, request, phone=None, password=None, **kwargs):
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return FaultCode.WRONG_PHONE_NUMBER.value

        if user.check_password(password):
            if self.user_can_authenticate(user):
                return user
            else:
                return UserSituation.INACTIVE_USER.value

        else:
            return FaultCode.INVALID_PASSWORD.value

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
