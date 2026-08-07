from yookassa import Configuration, Payment
from uuid import uuid4

class PaymentService:
    def __init__(self,
                 return_url: str,
                 bk_rp):
        self.return_url = return_url
        self.bk_rp = bk_rp

    async def create_booking_payment(self, booking_id: int) -> dict:
        full_bk = await self.bk_rp.get_full_bk(booking_id)
        ct = full_bk.catalog
        bk = full_bk.bk

        payment = Payment.create(
            {
                "amount": {
                    "value": f"{bk.price:.2f}",
                    "currency": "RUB",
                },
                "confirmation": {#ссылка для оплаты
                    "type": "redirect",
                    "return_url": self.return_url,
                },
                "capture": True,
                "description": f"Оплата № bk_id: {booking_id} : {ct.name}",
                "metadata" : {
                    "bk_id" : str(booking_id)
                }
            },
            str(uuid4()),
        )

        return {
            "payment_id": payment.id,
            "status": payment.status,
            "confirmation_id": payment.confirmation.confirmation_url
        }

    def get_payment(self, payment_id: str):
        return Payment.find_one(payment_id)