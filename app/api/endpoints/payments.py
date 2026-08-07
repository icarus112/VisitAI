import asyncio
import logging

from fastapi import APIRouter, status, Depends, HTTPException, Body
from yookassa.domain.exceptions import ApiError

from app.api.depencies import get_payment_service
from app.service.payment import PaymentService

router = APIRouter(prefix="/payments", tags=["Payment"])
logger = logging.getLogger(__name__)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_payment(
        booking_id: int = Body(embed=True),
        service: PaymentService = Depends(get_payment_service)):
    try:
        result = await service.create_booking_payment(booking_id)

        logger.info(
            "Создан платёж: booking_id=%s, payment_id=%s, status=%s",
            booking_id,
            result["payment_id"],
            result["status"],
        )

        return result

    except ApiError:
        logger.exception(
            "Ошибка ЮKassa при создании платежа: booking_id=%s",
            booking_id,
        )

    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Не удалось создать платёж",
    )

async def payment_webhook(
        notification: dict,
        service: PaymentService = Depends(get_payment_service)
):
    event = notification.get("event")
    payment_data = notification.get("object", {})
    payment_id = payment_data.get("id")

    if not payment_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not found payment_id"
        )

    payment_id = str(payment_id)

    try:
        payment = await asyncio.to_thread(
            service.get_payment,
            payment_id,
        )
    except Exception:
        logger.exception(
            "Не удалось проверить платёж в ЮKassa: payment_id=%s",
            payment_id,
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Не удалось проверить платёж",
        )

    if event == "payment.succeeded":
        if payment.status != "succeeded" or not payment.paid:
            logger.warning(
                "Webhook сообщает об оплате, но платёж не подтверждён: "
                "payment_id=%s status=%s paid=%s",
                payment.id,
                payment.status,
                payment.paid,
            )

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Статус платежа не подтверждён",
            )

        booking_id = payment.metadata.get("booking_id")

        logger.info(
            "Платёж подтверждён: payment_id=%s booking_id=%s amount=%s",
            payment.id,
            booking_id,
            payment.amount.value,
        )

    return {"status": "ok"}