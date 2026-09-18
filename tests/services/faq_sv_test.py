from unittest.mock import Mock, AsyncMock
import asyncio
import pytest

from app.service.faq import FaqService


@pytest.fixture
def faq_sv():
    faq_rp = AsyncMock()
    return FaqService(faq_rp)

@pytest.mark.asyncio
async def test_find_answer_wrong_intent(faq_sv: FaqService):
    input = Mock()
    input.intent = Mock(return_value="wrong_intent")

    result = await faq_sv.find_answer(input)

    assert result is None
    faq_sv.faq_rp.find_answer.assert_not_called()

@pytest.mark.asyncio
async def test_find_answer_none_faq(faq_sv: FaqService):
    input_data = Mock()

    input_data.intent = "faq"
    input_data.comment = ""
    input_data.search_keywords = []
    faq_sv.faq_rp.find_answer.return_value = None

    result = await faq_sv.find_answer(input_data)

    assert result is None
    faq_sv.faq_rp.find_answer.assert_awaited_once_with("")

@pytest.mark.asyncio
async def test_find_answer_success(faq_sv: FaqService):
    input_data = Mock()
    faq = Mock()

    input_data.intent = "faq"
    input_data.comment = "ac"
    input_data.search_keywords = []
    faq.answer = "answer_result"

    faq_sv.faq_rp.find_answer.return_value = faq

    result = await faq_sv.find_answer(input_data)

    assert result == faq.answer
    faq_sv.faq_rp.find_answer.assert_awaited_once_with("ac")



