from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

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
    password = serializers.CharField(write_only=True, validators=[validate_password])


class UserRegisterSerializer(IsValidMixin, PhoneSerializer):
    code = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
        allow_null=False,
        max_length=6,
        min_length=6,
    )

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Invalid OTP")
        return value

    class Meta:
        model = User
        fields = (
            "phone",
            "code",
        )
        read_only_fields = ("code",)


class UserUpdateSerializer(PasswordSerializer, serializers.ModelSerializer):
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
        instance.set_password(validated_data["password"])
        instance.first_name = validated_data["first_name"]
        instance.last_name = validated_data["last_name"]
        instance.is_active = True

        instance.save()
        # here a celery task can be run to delete work flow token in order to invoke it
        return instance


class UserLoginSerializer(IsValidMixin, PhoneSerializer, PasswordSerializer):
    class Meta:
        model = User
        fields = (
            "phone",
            "password",
        )


class JTISerializer(serializers.Serializer):
    jti = serializers.RegexField(regex=JTI_REGEX)
