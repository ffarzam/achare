from django.core.cache import caches
from rest_framework import exceptions, status
from rest_framework.generics import UpdateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from account.authentication import (
    AccessTokenAuthentication,
    PhoneAuthBackend,
    RefreshTokenAuthentication,
    WorkFlowTokenAuthentication,
)
from account.core.check_user_phone import (
    generate_otp_and_send,
    get_phone_from_serializer,
    save_otp_inside_cache,
)
from account.core.login import get_username_and_password_from_serializer
from account.core.register import (
    create_user_and_set_work_flow_token,
    get_code_and_phone_from_serializer,
    get_main_code_from_cache,
    is_otp_code_correct,
)
from account.core.tokens import (
    cache_key_parser,
    create_login_token,
    delete_all_sessions,
)
from account.custom_view import CustomAPIView
from account.enums.fault_code import FaultCode
from account.enums.user_state import UserSituation
from account.models import User
from account.permissions.active_user import IsActiveUser
from account.permissions.password_permissions import IsPasswordSet
from account.serializers import (
    CheckUserPhoneSerializer,
    JTISerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
    UserUpdateSerializer,
)
from account.utils import add_request_to_throttle


class CheckUserPhone(CustomAPIView):
    custom_throttle_scope = "check_phone"
    serializer_class = CheckUserPhoneSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = get_phone_from_serializer(serializer)

        user = User.default_objects.filter(phone=phone).values(
            "is_active", "password", "is_deleted"
        )
        send_opt = False
        response = None
        if user.exists():
            user_obj = user.get()
            add_request_to_throttle(request, self)
            add_request_to_throttle(request, self, phone)
            if user_obj.get("is_deleted"):
                response = Response(
                    {"message": [UserSituation.DELETED_ACCOUNT.value]},
                    status=status.HTTP_403_FORBIDDEN,
                )

            elif not user_obj.get("password") and not user_obj.get("is_active"):
                send_opt = True
                response = Response(
                    {"message": [UserSituation.NO_PASSWORD_FOUND.value]},
                    status=status.HTTP_403_FORBIDDEN,
                )
            elif not user_obj.get("is_active"):
                response = Response(
                    {"message": [UserSituation.INACTIVE_USER.value]},
                    status=status.HTTP_403_FORBIDDEN,
                )
            else:
                response = Response(
                    {"message": [UserSituation.LOGIN_REQUIRED.value]},
                    status=status.HTTP_200_OK,
                )

        else:
            send_opt = True

        if send_opt:
            sms_provider_result, code = generate_otp_and_send(phone)
            if sms_provider_result:
                save_otp_inside_cache(phone, code)

                add_request_to_throttle(request, self)
                add_request_to_throttle(request, self, phone)
                if not response:
                    response = Response(
                        {"message": [UserSituation.REGISTER_REQUIRED.value]},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                response = Response(
                    {"message": [FaultCode.SMS_PROVIDER_FAILURE.value]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return response


class UserRegister(CustomAPIView):
    custom_throttle_scope = "register"
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        user_input_phone, user_input_code = get_code_and_phone_from_serializer(
            serializer
        )
        main_code = get_main_code_from_cache(user_input_phone)
        if main_code is None:
            return Response(
                {"message": [UserSituation.OTP_EXPIRED.value]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if is_otp_code_correct(main_code, user_input_code):
            work_flow_token = create_user_and_set_work_flow_token(user_input_phone)
            data = {"work_flow_token": work_flow_token}
            return Response({"message": data}, status=status.HTTP_201_CREATED)

        # throttle can be here but implemented in serializer is_valid method
        # add_request_to_throttle(request, self)
        # add_request_to_throttle(request, self, user_input_phone)
        return Response(
            {"message": [UserSituation.WRONG_OTP.value]},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserUpdate(UpdateAPIView):
    authentication_classes = (WorkFlowTokenAuthentication,)
    permission_classes = (
        IsAuthenticated,
        IsPasswordSet,
    )
    serializer_class = UserUpdateSerializer
    http_method_names = ["patch"]

    def get_object(self):
        user = self.request.user
        self.check_object_permissions(self.request, user)
        return user


class UserLogin(CustomAPIView):
    custom_throttle_scope = "login"
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        phone, password = get_username_and_password_from_serializer(serializer)
        user = PhoneAuthBackend().authenticate(request, phone=phone, password=password)
        if user in [
            UserSituation.INACTIVE_USER.value,
            FaultCode.INVALID_PASSWORD.value,
            FaultCode.WRONG_PHONE_NUMBER.value,
        ]:
            add_request_to_throttle(request, self)
            if user in [
                FaultCode.INVALID_PASSWORD.value,
                UserSituation.INACTIVE_USER.value,
            ]:
                add_request_to_throttle(request, self, phone)

            raise exceptions.AuthenticationFailed(
                {"message": [UserSituation.WRONG_PASSWORD_OR_PHONE.value]}
            )
        access_token, refresh_token = create_login_token(request, user)
        data = {"access_token": access_token, "refresh_token": refresh_token}
        return Response({"message": data}, status=status.HTTP_200_OK)


class RefreshToken(APIView):
    authentication_classes = (RefreshTokenAuthentication,)
    permission_classes = (
        IsAuthenticated,
        IsActiveUser,
    )

    def post(self, request):
        user = request.user
        payload = request.auth

        jti = payload["jti"]
        caches["auth"].delete(f"user_{user.id} || {jti}")

        access_token, refresh_token = create_login_token(request, user)
        data = {"access": access_token, "refresh": refresh_token}

        return Response(data, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    authentication_classes = (RefreshTokenAuthentication,)
    permission_classes = (
        IsAuthenticated,
        IsActiveUser,
    )

    def get(self, request):
        payload = request.auth
        user = request.user
        jti = payload["jti"]
        caches["auth"].delete(f"user_{user.id} || {jti}")
        return Response(
            {"message": "Logged out successfully"}, status=status.HTTP_200_OK
        )


class CheckAllActiveLogin(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (
        IsAuthenticated,
        IsActiveUser,
    )

    def get(self, request):
        user = request.user

        active_login_data = []
        for key, value in (
            caches["auth"].get_many(caches["auth"].keys(f"user_{user.id} || *")).items()
        ):
            jti = cache_key_parser(key)[1]

            active_login_data.append(
                {
                    "jti": jti,
                    "user_agent": value,
                }
            )

        return Response(active_login_data, status=status.HTTP_200_OK)


class LogoutAll(APIView):
    authentication_classes = (RefreshTokenAuthentication,)
    permission_classes = (
        IsAuthenticated,
        IsActiveUser,
    )

    def get(self, request):
        user = request.user
        delete_all_sessions(user.id)
        return Response(
            {"message": UserSituation.LOGOUT_ALL_ACCOUNTS.value},
            status=status.HTTP_200_OK,
        )


class SelectedLogout(APIView):
    authentication_classes = (AccessTokenAuthentication,)
    permission_classes = (
        IsAuthenticated,
        IsActiveUser,
    )
    serializer_class = JTISerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        jti = serializer.validated_data["jti"]
        user = request.user

        caches["auth"].delete(f"user_{user.id} || {jti}")

        return Response(
            {"message": UserSituation.LOGOUT_CHOSEN_ACCOUNT.value},
            status=status.HTTP_200_OK,
        )


class DeleteAccount(DestroyAPIView):
    authentication_classes = (RefreshTokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    http_method_names = ["delete"]

    def get_object(self):
        user = self.request.user
        self.check_object_permissions(self.request, user)
        return user

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        delete_all_sessions(instance.id)
        return Response(
            data={"message": UserSituation.ACCOUNT_DELETED.value},
            status=status.HTTP_204_NO_CONTENT,
        )
