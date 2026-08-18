# import datetime
# from datetime import date
# from decimal import Decimal
#
# from sqlalchemy import select
#
# from app.core.enum import BookStatus
# from app.repository.catalog import CatalogRepos
# from app.repository.faq import FAQRepos
# from app.service.catalog import CatalogService
# from app.service.embedding import EmbeddingService
# from app.shemas.catalog import CatalogCreate, CatalogList
# from app.shemas.faq import FaqCreate, FaqList
# from app.shemas.record import BookingCreate, BookingList
# from app.database.async_engine import async_session
# from app.database.models import User, Catalog, Booking
#
# async def has_any(model) -> bool:
#     async with async_session() as session:
#         result = await session.execute(
#             select(model.id).limit(1)
#         )
#         return result.scalar_one_or_none() is not None
#
# async def fill_ct():
#     async with async_session() as session:
#         em_sv = EmbeddingService("intfloat/multilingual-e5-small")
#         ct_rp = CatalogRepos(session)
#         sv = CatalogService(ct_rp=ct_rp, em_sv=em_sv)
#
#         ct1 = CatalogCreate(
#             name="Пиллинг",
#             price=Decimal("1200"),
#             duration=45,
#             description="Процедура очищения кожи лица с удалением ороговевших клеток и улучшением состояния кожи.",
#             keywords=["пиллинг", "лицо", "очищение кожи", "уход за лицом", "косметология"],
#             client_phrases=[
#                 "хочу почистить лицо",
#                 "запишите на пилинг",
#                 "нужен уход за кожей лица",
#                 "хочу освежить кожу"
#             ]
#         )
#
#         ct2 = CatalogCreate(
#             name="Маникюр",
#             price=Decimal("1450"),
#             duration=60,
#             description="Уход за ногтями и кожей рук с обработкой кутикулы и покрытием лаком.",
#             keywords=["маникюр", "ногти", "руки", "лак", "кутикула"],
#             client_phrases=[
#                 "хочу сделать ногти",
#                 "запишите на маникюр",
#                 "нужно привести руки в порядок",
#                 "хочу красивый маникюр"
#             ]
#         )
#
#         ct3 = CatalogCreate(
#             name="Педикюр",
#             price=Decimal("1300"),
#             duration=45,
#             description="Уход за ногами, обработка стоп, ногтей и кутикулы.",
#             keywords=["педикюр", "ноги", "стопы", "ногти", "уход за ногами"],
#             client_phrases=[
#                 "хочу сделать ножки",
#                 "запишите на педикюр",
#                 "нужно привести ноги в порядок",
#                 "хочу уход за стопами"
#             ]
#         )
#
#         ct4 = CatalogCreate(
#             name="Наращивание ресниц",
#             price=Decimal("1800"),
#             duration=45,
#             description="Увеличение длины и объема ресниц с помощью искусственных материалов.",
#             keywords=["ресницы", "наращивание ресниц", "взгляд", "объем", "красота"],
#             client_phrases=[
#                 "хочу длинные ресницы",
#                 "запишите на ресницы",
#                 "сделайте объемные ресницы",
#                 "хочу наращивание"
#             ]
#         )
#
#         ct5 = CatalogCreate(
#             name="стрижка мужская",
#             price=Decimal("1000"),
#             duration=50,
#             description="Мужская стрижка машинкой и ножницами с оформлением прически.",
#             keywords=["стрижка", "волосы", "барбер", "мужская стрижка", "парикмахер"],
#             client_phrases=[
#                 "хочу подстричься",
#                 "нужно укоротить волосы",
#                 "запишите на мужскую стрижку",
#                 "сделайте мне прическу"
#             ]
#         )
#
#         ct6 = CatalogCreate(
#             name="Массаж",
#             price=Decimal("1600"),
#             duration=90,
#             description="Расслабляющий массаж тела для снятия напряжения и усталости.",
#             keywords=["массаж", "спина", "расслабление", "тело", "мышцы"],
#             client_phrases=[
#                 "болит спина",
#                 "хочу массаж",
#                 "нужно расслабиться",
#                 "запишите на массаж"
#             ]
#         )
#
#         ct7 = CatalogCreate(
#             name="стрижка женская",
#             price=Decimal("2600"),
#             duration=50,
#             description="Женская стрижка с подбором формы и укладкой волос.",
#             keywords=["стрижка", "волосы", "женская стрижка", "укладка", "парикмахер"],
#             client_phrases=[
#                 "хочу изменить прическу",
#                 "нужно подстричь волосы",
#                 "запишите на женскую стрижку",
#                 "хочу новую стрижку"
#             ]
#         )
#
#         ct8 = CatalogCreate(
#             name="Окрашивание волос женское",
#             price=Decimal("3600"),
#             duration=60,
#             description="Изменение цвета волос с использованием профессиональных красителей.",
#             keywords=["окрашивание", "волосы", "краска", "блонд", "цвет волос"],
#             client_phrases=[
#                 "хочу покрасить волосы",
#                 "изменить цвет волос",
#                 "запишите на окрашивание",
#                 "хочу стать блондинкой"
#             ]
#         )
#
#         ct9 = CatalogCreate(
#             name="Уход за ресницами",
#             price=Decimal("2200"),
#             duration=50,
#             description="Укрепление, восстановление и уход за натуральными ресницами.",
#             keywords=["ресницы", "ламинирование", "уход", "восстановление", "взгляд"],
#             client_phrases=[
#                 "хочу красивые ресницы",
#                 "нужен уход за ресницами",
#                 "запишите на ламинирование",
#                 "укрепить ресницы"
#             ]
#         )
#
#         ct10 = CatalogCreate(
#             name="Мужское окрашивание волос",
#             price=Decimal("2300"),
#             duration=70,
#             description="Окрашивание мужских волос для смены цвета или маскировки седины.",
#             keywords=["мужское окрашивание", "волосы", "седина", "краска", "цвет волос"],
#             client_phrases=[
#                 "хочу покрасить волосы",
#                 "закрасить седину",
#                 "изменить цвет волос",
#                 "запишите на окрашивание"
#             ]
#         )
#
#         cts = CatalogList(item=[ct1, ct2, ct3, ct4, ct5,
#                                 ct6, ct7, ct8, ct9, ct10])
#         n = 1
#         for c in cts.item:
#
#             embedding = await em_sv.embed_catalog(c)
#
#             new_ct = await ct_rp.create_ct(c, embedding)
#
#             print("ct: ", n)
#             n+=1
#
#         await session.commit()
#
# async def fill_faq():
#     async with async_session() as session:
#         faq_rp = FAQRepos(session)
#
#         faq1 = FaqCreate(
#             question="Какой у вас график?",
#             keywords=["график", "работаете", "время", "открыты", "воскресенье"],
#             answer="Мы работаем ежедневно с 10:00 до 20:00."
#         )
#
#         faq2 = FaqCreate(
#             question="Где вы находитесь?",
#             keywords=["адрес", "где", "локация", "местоположение", "находитесь"],
#             answer="Мы находимся по адресу: ул. Примерная, 10."
#         )
#
#         faq3 = FaqCreate(
#             question="Можно ли оплатить картой?",
#             keywords=["оплата", "карта", "наличные", "перевод", "предоплата"],
#             answer="Да, оплатить можно картой, наличными или переводом, также в нашем боте через Юкасса"
#         )
#
#         faq4 = FaqCreate(
#             question="Нужно ли вносить предоплату?",
#             keywords=["предоплата", "залог", "оплата заранее", "бронь", "аванс"],
#             answer="Обычно предоплата не требуется. Если для конкретной услуги нужна предоплата, администратор предупредит заранее."
#         )
#
#         faq5 = FaqCreate(
#             question="Как отменить запись?",
#             keywords=["отмена", "отменить", "запись", "не приду", "отказаться"],
#             answer="Отменить запись можно через раздел «Мои записи» или написав администратору."
#         )
#
#         faq6 = FaqCreate(
#             question="Можно ли перенести запись?",
#             keywords=["перенос", "перенести", "другое время", "изменить запись", "поменять время"],
#             answer="Да, запись можно перенести. Это делается через раздел «Мои записи» или написав администратору."
#         )
#
#         faq7 = FaqCreate(
#             question="Что делать, если я опаздываю?",
#             keywords=["опаздываю", "задерживаюсь", "опоздание", "позже", "не успеваю"],
#             answer="Если вы опаздываете, пожалуйста, предупредите заранее администратора. При сильном опоздании запись может быть перенесена."
#         )
#
#         faq8 = FaqCreate(
#             question="Как узнать цену услуги?",
#             keywords=["цена", "стоимость", "сколько стоит", "прайс", "услуги"],
#             answer="Цены можно посмотреть в каталоге услуг. Также вы можете написать название услуги, и бот подскажет информацию."
#         )
#
#         faq9 = FaqCreate(
#             question="Сколько длится процедура?",
#             keywords=["длительность", "сколько длится", "время процедуры", "долго", "минут"],
#             answer="Длительность зависит от выбранной услуги. Обычно время указано в карточке услуги."
#         )
#
#         faq10 = FaqCreate(
#             question="Можно ли записаться к конкретному мастеру?",
#             keywords=["мастер", "конкретный мастер", "к кому", "специалист", "выбрать мастера"],
#             answer="Да, если нужный мастер доступен. Укажите имя мастера при записи или напишите администратору."
#         )
#
#         faq11 = FaqCreate(
#             question="Можно ли прийти без записи?",
#             keywords=["без записи", "сразу прийти", "живая очередь", "свободно", "сегодня"],
#             answer="Лучше записаться заранее, чтобы мы точно могли принять вас в удобное время."
#         )
#
#         faq12 = FaqCreate(
#             question="Как посмотреть свои записи?",
#             keywords=["мои записи", "посмотреть запись", "когда я записан", "записи", "проверить запись"],
#             answer="Посмотреть свои записи можно через кнопку «Мои записи» в главном меню."
#         )
#
#         faq13 = FaqCreate(
#             question="Можно ли записаться на сегодня?",
#             keywords=["сегодня", "на сегодня", "свободное время", "записаться сегодня", "есть места"],
#             answer="Да, если есть свободные места. Напишите желаемую услугу и время, бот проверит возможность записи."
#         )
#
#         faq14 = FaqCreate(
#             question="Как связаться с администратором?",
#             keywords=["админ", "администратор", "связаться", "контакты", "поддержка"],
#             answer="Вы можете написать администратору через кнопку «Связаться с администратором» в главном меню."
#         )
#
#         faq15 = FaqCreate(
#             question="Какие услуги у вас есть?",
#             keywords=["услуги", "каталог", "что есть", "список услуг", "процедуры"],
#             answer="Список услуг можно посмотреть в каталоге. Нажмите кнопку «Каталог услуг» в главном меню."
#         )
#
#         faqs = FaqList(item=[faq1, faq2, faq3, faq4, faq5,
#                             faq6, faq7, faq8, faq9, faq10,
#                             faq11, faq12, faq13, faq14, faq15])
#
#         for f in faqs.item:
#             new_faq = await faq_rp.create_faq(f)
#
#         await session.commit()
#
# async def fill_bk():
#     async with async_session() as session:
#         us_result = await session.execute(
#             select(User).limit(1)
#         )
#         user = us_result.scalar_one_or_none()
#
#         if user is None:
#             print("Нельзя создать записи: в БД нет пользователей")
#             return
#
#         ct_result = await session.execute(
#             select(Catalog).order_by(Catalog.id).limit(5)
#         )
#         catalogs = list(ct_result.scalars().all())
#
#         if len(catalogs) < 5:
#             print("Нельзя создать записи: в БД меньше 5 услуг")
#             return
#
#         today = date.today()
#
#         bk1 = BookingCreate(
#             user_id=user.id,
#             catalog_id=catalogs[0].id,
#             date=today + datetime.timedelta(days=1),
#             time=datetime.time(hour=10, minute=0),
#             status=BookStatus.PENDING,
#             comment="Хочу попасть к мастеру Анне, если будет свободное время."
#         )
#
#         bk2 = BookingCreate(
#             user_id=user.id,
#             catalog_id=catalogs[1].id,
#             date=today + datetime.timedelta(days=2),
#             time=datetime.time(hour=12, minute=30),
#             status=BookStatus.UNPAID,
#             comment="Возможно, немного опоздаю на 5-10 минут."
#         )
#
#         bk3 = BookingCreate(
#             user_id=user.id,
#             catalog_id=catalogs[2].id,
#             date=today + datetime.timedelta(days=3),
#             time=datetime.time(hour=15, minute=0),
#             status=BookStatus.PAID,
#             comment="Прошу записать к любому свободному мастеру."
#         )
#
#         bk4 = BookingCreate(
#             user_id=user.id,
#             catalog_id=catalogs[3].id,
#             date=today - datetime.timedelta(days=1),
#             time=datetime.time(hour=14, minute=0),
#             status=BookStatus.COMPLETED,
#             comment="Хочу уточнить детали процедуры перед началом."
#         )
#
#         bk5 = BookingCreate(
#             user_id=user.id,
#             catalog_id=catalogs[4].id,
#             date=today + datetime.timedelta(days=5),
#             time=datetime.time(hour=18, minute=30),
#             status=BookStatus.CANCELLED,
#             comment="Если возможно, поставьте запись ближе к вечеру."
#         )
#
#         bks = BookingList(item=[bk1, bk2, bk3, bk4, bk5])
#         n = 1
#
#         for b in bks.item:
#             new_bk = Booking(
#                 user_id=b.user_id,
#                 catalog_id=b.catalog_id,
#                 date=b.date,
#                 time=b.time,
#                 status=b.status,
#                 comment=b.comment
#             )
#             session.add(new_bk)
#             print("bk:", n)
#             n += 1
#
#         await session.commit()
#         print("Записи успешно созданы")