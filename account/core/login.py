from typing import Tuple


def get_username_and_password_from_serializer(serializer) -> Tuple[str, str]:
    phone = serializer.validated_data.get("phone")
    password = serializer.validated_data.get("password")
    return phone, password
