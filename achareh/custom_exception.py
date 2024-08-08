from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class ExpiredAccessTokenError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _("Access Token Has Been Expired")
    default_code = "expired_access_token"


class ExpiredRefreshTokenError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _("Refresh Token Has Been Expired, Please Login Again")
    default_code = "expired_refresh_token"


class ExpiredWorkFlowTokenError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _("Work Flow Token Has Been Expired")
    default_code = "expired_work_flow_token"


class InvalidTokenError(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _("Invalid Token, Please Login Again")
    default_code = "invalid_token"


class UserNotFound(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _("User Not Found")
    default_code = "user_not_found"


class CommonError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("An error occurred")
    default_code = "error"
