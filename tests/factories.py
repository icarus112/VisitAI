from datetime import datetime
from decimal import Decimal
from itertools import count

from app.core.enum import BookStatus, PaymentMethod, AdminRole
from app.database import User, Catalog, Booking, Admin
from app.repository import booking


class ModelFactory:
    _tg_id_counter = count(10000)
    base_time = datetime(2038, 1, 19, 3, 14, 8) #ВЫ НАШЛИ ПОСХАЛКУ)


    def __init__(self, session):
        self.session = session

    async def create_user(self,
                          tg_id=None,
                          name="gay",
                          phone="6769") -> User:
        if tg_id is None:
            tg_id = next(self._tg_id_counter)

        user = User(
            tg_id=tg_id,
            name=name,
            phone=phone
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def create_catalog(self,
                             name="smth",
                             price=Decimal('300'),
                             duration=67,
                             description="description",
                             keywords=None,
                             client_phrases=None,
                             embedding=None
                             ) -> Catalog:

        if keywords is None:
            keywords = ["ka", "ds"]

        if client_phrases is None:
            client_phrases = ["ka", "ds"]

        if embedding is None:
            embedding = [6.7] * 384

        catalog = Catalog(
            name=name,
            price=price,
            duration=duration,
            description=description,
            keywords=keywords,
            client_phrases=client_phrases,
            embedding=embedding
        )

        self.session.add(catalog)
        await self.session.flush()
        return catalog

    async def create_booking(self,
                             user=None,
                             catalog=None,
                             scheduled_at=None,
                             price=Decimal('300'),
                             status=BookStatus.CONFIRMED,
                             payment_method=PaymentMethod.ONLINE,
                             comment=None) -> Booking:

        if user is None:
            user = await self.create_user()

        if catalog is None:
            catalog =await self.create_catalog()

        if scheduled_at is None:
            scheduled_at = datetime.now()

        if comment is None:
            comment = "comment"

        booking = Booking(
            user_id=user.id,
            catalog_id=catalog.id,
            scheduled_at=scheduled_at,
            price=price,
            status=status,
            payment_method=payment_method,
            comment=comment
        )

        self.session.add(booking)
        await self.session.flush()
        return booking

    async def create_admin(self,
                           tg_id=None,
                           name="smbd",
                           role=AdminRole.ADMIN) -> Admin:
        if tg_id is None:
            tg_id = next(self._tg_id_counter)

        admin = Admin(
            tg_id=tg_id,
            name=name,
            role=role
        )

        self.session.add(admin)
        await self.session.flush()
        return admin


