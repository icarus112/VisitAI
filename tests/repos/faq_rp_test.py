import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Faq
from app.repository.faq import FAQRepos
from app.shemas.faq import FaqCreate

@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_create_faq(session_test: AsyncSession):
    faq_repos = FAQRepos(session_test)

    faq = FaqCreate(
        question="question",
        keywords=["keyword1", "keyword2"],
        answer="answer",
    )

    result = await faq_repos.create_faq(faq)

    assert result.question == "question"
    assert result.keywords == ["keyword1", "keyword2"]
    assert result.answer == "answer"


#мне было лень, поэтому сгенерил этот тест, не зря же у меня подписка на чатжпт
@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_find_answer(session_test: AsyncSession):
    faq_repos = FAQRepos(session_test)

    target = Faq(
        question="Как отменить запись?",
        keywords=["отмена", "запись", "бронирование"],
        answer="Для отмены записи нажмите кнопку отмены.",
        search_text="как отменить запись отмена записи отменить бронирование",
    )

    similar = Faq(
        question="Как записаться?",
        keywords=["запись", "бронирование"],
        answer="Выберите услугу и время.",
        search_text="как записаться на услугу запись бронирование",
    )

    different = Faq(
        question="Сколько стоит массаж?",
        keywords=["массаж", "цена"],
        answer="Стоимость массажа указана в каталоге.",
        search_text="массаж цена стоимость услуги",
    )

    session_test.add_all([
        target,
        similar,
        different,
    ])

    await session_test.flush()

    result = await faq_repos.find_answer(
        "как отменить запись отмена записи отменить бронирование"
    )

    assert result is not None
    assert result.id == target.id
    assert result.answer == target.answer