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

@pytest.mark.asyncio(
    loop_scope = "session"
)
async def test_get_ct_page(session_test: AsyncSession):
    factory = ModelFactory(session_test)
    ct_rp = CatalogRepos(session_test)

    ct_1 = await factory.create_catalog()
    ct_2 = await factory.create_catalog()
    ct_3 = await factory.create_catalog()
    ct_4 = await factory.create_catalog()

    cts = await ct_rp.get_ct_page(page=1, per_page=2)

    assert len(cts) == 2
    assert [ct.id  for ct in cts] == [ct_3.id, ct_4.id]

@pytest.mark.asyncio(
    loop_scope = "session"
)
async def test_find_ilike(session_test: AsyncSession):
    factory = ModelFactory(session_test)
    ct_rp = CatalogRepos(session_test)

    ct_1 = await factory.create_catalog(name="ct_1")
    ct_2 = await factory.create_catalog(name="ct_2")
    ct_3 = await factory.create_catalog(name="smth")

    cts = await ct_rp.find_ilike("ct")

    assert len(cts) == 2
    assert [ct.id for ct in cts] == [ct_1.id, ct_2.id]

@pytest.mark.asyncio(
    loop_scope = "session"
)
async def test_find_name_fuzzy(session_test: AsyncSession):
    factory = ModelFactory(session_test)
    ct_rp = CatalogRepos(session_test)

    ct_1 = await factory.create_catalog(name="котость")
    ct_2 = await factory.create_catalog(name="кот")
    ct_3 = await factory.create_catalog(name="нечто")

    result = await ct_rp.find_name_fuzzy("кот")

    assert len(result) == 2
    assert [ct.id for ct in result] == [ct_2.id, ct_1.id]


@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_embedding_search(session_test: AsyncSession):
    factory = ModelFactory(session_test)
    ct_rp = CatalogRepos(session_test)

    similar = await factory.create_catalog(
        embedding=[0.9, 0.1] + [0.0] * 382
    )
    target = await factory.create_catalog(
        embedding=[1.0, 0.2] + [0.0] * 382
    )
    different = await factory.create_catalog(
        embedding=[0.1, 0.9] + [0.0] * 382
    )

    result = await ct_rp.embedding_search(
        query_vector=target.embedding,
        limit=2
    )

    await session_test.refresh(similar)
    await session_test.refresh(target)

    assert len(result) == 2
    assert [ct[0].id for ct in result] == [target.id, similar.id]