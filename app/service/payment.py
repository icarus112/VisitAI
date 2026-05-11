from yookassa import Configuration, Payment, payment
from uuid import uuid4

class PaymentService:
    def __init__(self, shop_id: str,
                 secret_key: str,
                 return_url: str):
        Configuration.account_id = shop_id
        Configuration.secret_key = secret_key
        Configuration.return_url = return_url

    def create_booking_payment(self,
                               booking_id: int,
                               amount: int | float,
                               description: str):
        payment = Payment.create(
            {
                "amount": {

                },
                "confirmation": {#ссылка для оплаты

                },
                "capture": True,
                "description": description,
                "metadata" : {

                }
            },
            uuid4()
        )

        return {
            "payment_id": payment.id,
            "status": payment.status,
            "confirmation_id": payment.confirmation.confirmation_url
        }