import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.catalog import CatalogRepos
from app.shemas.catalog import CatalogCreate
from tests.factories import ModelFactory


@pytest.mark.asyncio(
    loop_scope = "session"
)
async def test_create_ct(session_test: AsyncSession):
    factory = ModelFactory(session_test)
    ct_rp = CatalogRepos(session_test)

    ct = CatalogCreate(
        name = "ct_1",
        price = Decimal("450"),
        duration = 75,

        description = "description_1",
        keywords = ["keywords_1", "keywords_2"],
        client_phrases=["phrase_1", "phrase_2"]
    )

    res = await ct_rp.create_ct(ct, [6.7] * 384)
    await session_test.flush()
    await session_test.refresh(res)

    assert res.id is not None
    assert res.name == ct.name
    assert res.price == ct.price
    assert len(res.embedding) == 384

# @pytest.mark.asyncio(
#     loop_scope = "session"
# )
# async def test_get_all(session_test: AsyncSession):