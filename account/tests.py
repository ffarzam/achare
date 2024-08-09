import os

from django.test import TestCase

# Create your tests here.

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch


from .enums.fault_code import FaultCode
from .enums.user_state import UserSituation
from .models import User


class CheckUserPhoneTests(APITestCase):
    # @classmethod
    # def setUpClass(cls):
    #     os.environ['DJANGO_SETTINGS_MODULE'] = 'achareh.settings'
    #     super().setUpClass()

    def setUp(self):
        self.url = reverse("account:check_phone")
        self.valid_phone = "09117200513"
        self.deleted_user = User.objects.create(
            phone=self.valid_phone, is_active=True, is_deleted=True
        )
        self.inactive_user = User.objects.create(
            phone="09876543210", is_active=False, password="some_password"
        )
        self.no_password_user = User.objects.create(
            phone="09119876543",
            is_active=False,
        )
        self.active_user = User.objects.create(
            phone="09111234567", is_active=True, password="some_password"
        )

    @patch("account.mixins.generate_otp_and_send")
    def test_new_user_otp_sent(self, mock_generate_otp_and_send):
        mock_generate_otp_and_send.return_value = (True, "123456")
        data = {"phone": "09333696798"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data["message"][0], UserSituation.REGISTER_REQUIRED.value
        )

    @patch("account.mixins.generate_otp_and_send")
    def test_deleted_user(self, mock_generate_otp_and_send):
        data = {"phone": self.valid_phone}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["message"][0], UserSituation.DELETED_ACCOUNT.value
        )

    @patch("account.mixins.generate_otp_and_send")
    def test_inactive_user_no_password(self, mock_generate_otp_and_send):
        mock_generate_otp_and_send.return_value = (True, "123456")
        data = {"phone": self.no_password_user.phone}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data["message"][0], UserSituation.NO_PASSWORD_FOUND.value
        )

    @patch("account.mixins.generate_otp_and_send")
    def test_inactive_user(self, mock_generate_otp_and_send):
        data = {"phone": self.inactive_user.phone}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data["message"][0], UserSituation.INACTIVE_USER.value)

    def test_active_user(self):
        data = {"phone": self.active_user.phone}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["message"][0], UserSituation.LOGIN_REQUIRED.value
        )

    @patch("account.mixins.generate_otp_and_send")
    def test_otp_failure(self, mock_generate_otp_and_send):
        mock_generate_otp_and_send.return_value = (False, "123456")
        data = {"phone": "09333656799"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["message"][0], FaultCode.SMS_PROVIDER_FAILURE.value
        )
