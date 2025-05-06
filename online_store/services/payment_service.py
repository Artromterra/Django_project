import requests
import uuid
import os

YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID')
YOOKASSA_API_KEY = os.getenv('YOOKASSA_API_KEY')

class PaymentService:
    def __init__(self):
        self.api_url = 'https://api.yookassa.ru/v3/payments'
        self.shop_id = YOOKASSA_SHOP_ID
        self.api_key = YOOKASSA_API_KEY

    def pay_order(self, cart_number, expiry_month, expiry_year, cvc, total_price, order_id):
        headers = {
            'Content-Type': 'application/json',
            'Idempotence-Key': str(uuid.uuid4()),
        }

        data = {
            "amount": {
                "value": str(total_price),
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card",
                "card": {
                    "number": cart_number,
                    "expiry_month": expiry_month,
                    "expiry_year": expiry_year,
                    "cvc": cvc
                }
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "http://127.0.0.1:8000/shop/order-confirm/payment/progressPayment"
            },
            "description": f"Оплата заказа #{order_id}",
            "capture": True
        }

        response = requests.post(
            self.api_url,
            json=data,
            headers=headers,
            auth=(self.shop_id, self.api_key)
        )

        if response.status_code in (200, 201):
            return response.json()
        else:
            print("Ошибка при оплате через ЮKassa:", response.text)
            response.raise_for_status()

    def check_payment_status(self, payment_id):
        url = f"{self.api_url}/{payment_id}"
        response = requests.get(
            url,
            auth=(self.shop_id, self.api_key)
        )

        if response.status_code in (200, 201):
            return response.json()
        else:
            print("Ошибка при проверке статуса оплаты:", response.text)
            response.raise_for_status()
