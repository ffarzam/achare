from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from account.core.tokens import delete_work_flow_token
from account.mixins import IsValidMixin
from account.models import User
from account.utils import JTI_REGEX, PHONE_REGEX


class PhoneSerializer(serializers.Serializer):
    phone = serializers.RegexField(
        regex=PHONE_REGEX,
        error_messages={
            "invalid": "Phone number must be entered in the format: '09*********'."
        },
    )


class CheckUserPhoneSerializer(PhoneSerializer):
    pass


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        required=True,
        allow_blank=False,
        allow_null=False,
    )


class UserRegisterSerializer(IsValidMixin, PhoneSerializer):
    code = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
        allow_null=False,
        max_length=6,
        min_length=6,
    )

    def validate_phone(self, value):
        user = (
            User.default_objects.filter(phone=value)
            .values("is_deleted", "is_active", "password")
            .first()
        )
        if user and user.get("is_deleted"):
            raise serializers.ValidationError("Deleted Account!")
        elif user and user.get("password") and not user.get("is_active"):
            raise serializers.ValidationError("Your Account Is Not Active Exists!")
        elif user and user.get("password") and user.get("is_active"):
            raise serializers.ValidationError("Account Already Exists!")

        return value

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Invalid OTP")
        return value


class UserUpdateSerializer(PasswordSerializer, serializers.ModelSerializer):

    first_name = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
        allow_null=False,
        required=True,
    )
    last_name = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
        allow_null=False,
        required=True,
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "password",
        )

    def validate_first_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("First name is not valid")
        return value.strip()

    def validate_last_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Last name is not valid")
        return value.strip()

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.is_active = True
        instance.save()
        # here a celery task can be run to delete work flow token in order to invoke it
        delete_work_flow_token(instance.id)
        return instance


class UserLoginSerializer(IsValidMixin, PhoneSerializer, PasswordSerializer):
    pass


class JTISerializer(serializers.Serializer):
    jti = serializers.RegexField(regex=JTI_REGEX)
