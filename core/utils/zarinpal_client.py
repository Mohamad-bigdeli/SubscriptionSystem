from __future__ import annotations

import json

from django.conf import settings
import requests


class ZarinpalClient:

    def __init__(self, timeout=10.0):
        self.merchant_id = settings.ZARINPAL["MERCHANT_ID"]
        self.sandbox = settings.ZARINPAL["SANDBOX"]
        self.timeout = timeout

        self.base_api_url = (
            "https://payment.zarinpal.com/pg/v4/payment/"  # Production
            if not self.sandbox
            else "https://sandbox.zarinpal.com/pg/v4/payment/"  # Sandbox
        )

        self.payment_gateway_url = (
            "https://payment.zarinpal.com/pg/StartPay/"  # Production
            if not self.sandbox
            else "https://sandbox.zarinpal.com/pg/StartPay/"  # Sandbox
        )

    def request_payment(self, amount, callback_url, description="Request Payment",
                        mobile=None, email=None,metadata=None,):
        url = self.base_api_url + "request.json"
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "callback_url": callback_url,
            "description": description,
            "currency": "IRT",
        }
        if mobile:
            payload["mobile"] = mobile
        if email:
            payload["email"] = email
        if metadata:
            payload["metadata"] = metadata

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            response = requests.post(
                url,
                data=json.dumps(payload),
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            if data.get("data", {}).get("code") != 100:
                error_msg = data.get("errors", {}).get("message", "Payment request failed")
                raise Exception(f"ZarinPal Error: {error_msg} (Code: {data.get('data', {}).get('code')})")

            authority = data["data"]["authority"]
            payment_url = f"{self.payment_gateway_url}{authority}"

            return {
                "authority": authority,
                "payment_url": payment_url,
                "raw_response": data,
            }
        except requests.Timeout:
            raise Exception("Payment request timed out")
        except requests.RequestException as e:
            raise Exception(f"Network error: {e!s}")

    def verify_payment(self, authority, amount):
        url = self.base_api_url + "verify.json"
        payload = {
            "merchant_id": self.merchant_id,
            "amount": amount,
            "authority": authority,
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            response = requests.post(
                url,
                data=json.dumps(payload),
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            if data.get("data").get("code") != 100:
                error_msg = data.get("errors")
                raise Exception(f"ZarinPal Error: {error_msg} (Code: {data.get('data').get('code')})")

            return {
                "ref_id": data["data"]["ref_id"],
                "raw_response": data,
            }
        except requests.Timeout:
            raise Exception("Verification request timed out")
        except requests.RequestException as e:
            raise Exception(f"Network error: {e!s}")

