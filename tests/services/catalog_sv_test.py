from decimal import Decimal
from unittest.mock import AsyncMock, Mock
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.service.catalog import CatalogService
from app.shemas.ai import AICatalogDescription, AIIntentBooking
from app.shemas.catalog import CatalogCreate
from tests.factories import ModelFactory


@pytest.fixture
def catalog_sv() -> CatalogService:
    ct_rp = AsyncMock()
    em_sv = AsyncMock()
    return CatalogService(ct_rp, em_sv)

@pytest.mark.parametrize("bad_value",[
    None, '-12'])
def test_str_to_decimal_bad_value(bad_value: str | None,
                                  catalog_sv: CatalogService):
     with pytest.raises(ValueError):
         catalog_sv.str_to_decimal(bad_value)

@pytest.mark.parametrize("value, expected",[
    ('13,54', Decimal('13.5')),
    (Decimal('32.57'), Decimal('32.6')),
    ('22.95', Decimal('23'))
])
def test_str_to_decimal_success(value: str|Decimal,
                                expected: Decimal,
                                catalog_sv: CatalogService):
    res =  catalog_sv.str_to_decimal(value)
    assert res == expected

@pytest.mark.asyncio
@pytest.mark.parametrize("bad_value",[
    [None, 500, 30, 123, "ai_res"],
    ["name", 500, 30, 123, None],
    ["name", 500, "duration", 123, "ai_res"],
    ["name", 500, -30, 123, "ai_res"],
])
async def test_create_ct_bad_value(bad_value: list,
                                   catalog_sv: CatalogService):
    with pytest.raises(ValueError):
        await catalog_sv.create_ct(bad_value[0],
                             bad_value[1],
                             bad_value[2],
                             bad_value[3],
                             bad_value[4])
    catalog_sv.ct_rp.create_ct.assert_not_awaited()

@pytest.mark.asyncio
async def test_create_ct_side_error(catalog_sv: CatalogService):
    catalog_sv.em_sv.embed_catalog.return_value = Mock()
    catalog_sv.ct_rp.create_ct.side_effect = Exception("test error")
    with pytest.raises(Exception, match="test error"):
        await catalog_sv.create_ct(
            "name", 500, 30, 123,
            AICatalogDescription(
                description="description",
                keywords= ["1", "2"],
                client_phrases=["3, 4"]
            )
        )

@pytest.mark.asyncio
async def test_create_ct_embed_error(catalog_sv):
    catalog_sv.em_sv.embed_catalog.side_effect = Exception("embedding error")

    with pytest.raises(Exception, match="embedding error"):
        await catalog_sv.create_ct(
            "name",
            500,
            30,
            123,
            AICatalogDescription(
                description="description",
                keywords=["1"],
                client_phrases=["2"]
            )
        )



@pytest.mark.asyncio(
    loop_scope="session"
)
async def test_create_ct_success(session_test: AsyncSession,
                                 catalog_sv: CatalogService):
    factory = ModelFactory(session_test)
    ai_data = AICatalogDescription(
                description="description",
                keywords= ["1", "2"],
                client_phrases=["3, 4"]
            )
    my_catalog = await factory.create_catalog(
        name="name",
        price=500,
        duration=30,
        description=ai_data.description,
        keywords=ai_data.keywords,
        client_phrases=ai_data.client_phrases,
        embedding= None)
    ct_data = CatalogCreate(
            name=my_catalog.name,
            price=my_catalog.price,
            duration=my_catalog.duration,
            description=my_catalog.description,
            keywords=my_catalog.keywords,
            client_phrases=my_catalog.client_phrases,
        )

    catalog_sv.em_sv.embed_catalog.return_value = my_catalog.embedding
    catalog_sv.ct_rp.create_ct.return_value = my_catalog
    await catalog_sv.create_ct(
        name=my_catalog.name,
        price=my_catalog.price,
        duration=my_catalog.duration,
        ad_tg_id=123,
        ai_res=ai_data
    )
    catalog_sv.ct_rp.create_ct.assert_awaited_once_with(
        ct_data,
        my_catalog.embedding
    )
    catalog_sv.em_sv.embed_catalog.assert_awaited_once_with(
        ct_data
    )

@pytest.mark.asyncio
async def test_page_data_empty(catalog_sv):
    catalog_sv.ct_rp.count_ct.return_value = 0

    result = await catalog_sv.page_data(0)

    assert result == (
        [],
        0,
        0
    )

    catalog_sv.ct_rp.get_ct_page.assert_not_awaited()

@pytest.mark.asyncio
async def test_page_data_negative_page(catalog_sv: CatalogService):
    catalog_sv.ct_rp.count_ct.return_value = 10
    catalog_sv.ct_rp.get_ct_page.return_value = []

    result = await catalog_sv.page_data(
        page=-5,
        per_page=5
    )

    assert result[1] == 0

    catalog_sv.ct_rp.get_ct_page.assert_awaited_once_with(
        0,
        5
    )

@pytest.mark.asyncio
async def test_page_data_page_out_of_range(catalog_sv: CatalogService):
    catalog_sv.ct_rp.count_ct.return_value = 10
    catalog_sv.ct_rp.get_ct_page.return_value = []

    result = await catalog_sv.page_data(
        page=10,
        per_page=5
    )

    assert result[1] == 1
    assert result[2] == 2

    catalog_sv.ct_rp.get_ct_page.assert_awaited_once_with(
        1,
        5
    )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "page, expected_page",
    [
        (-1, 0),
        (-100, 0),
        (0, 0),
        (1, 1),
        (100, 2),
    ]
)
async def test_page_data_page_normalization(
        catalog_sv,
        page,
        expected_page
):
    catalog_sv.ct_rp.count_ct.return_value = 15
    catalog_sv.ct_rp.get_ct_page.return_value = []

    result = await catalog_sv.page_data(page)

    assert result[1] == expected_page

@pytest.mark.asyncio
async def test_page_data_success(catalog_sv: CatalogService):
    catalog_sv.ct_rp.count_ct.return_value = 12
    catalogs = ["ct1", "ct2", "ct3"]

    catalog_sv.ct_rp.get_ct_page.return_value = catalogs

    result = await catalog_sv.page_data(
        page=1,
        per_page=5
    )

    assert result == (
        catalogs,
        1,
        3
    )

    catalog_sv.ct_rp.count_ct.assert_awaited_once()
    catalog_sv.ct_rp.get_ct_page.assert_awaited_once_with(
        1,
        5
    )

@pytest.mark.asyncio
async def test_find_name_ilike(catalog_sv: CatalogService):
    cts = [Mock()]
    catalog_sv.ct_rp.find_ilike.return_value = cts
    res = await catalog_sv.find_by_name("my_name")

    assert res == cts
    catalog_sv.ct_rp.find_name_fuzzy.assert_not_awaited()

@pytest.mark.asyncio
async def test_find_name_ilike(catalog_sv: CatalogService):
    cts = [Mock()]
    catalog_sv.ct_rp.find_ilike.return_value = []
    catalog_sv.ct_rp.find_name_fuzzy.return_value = cts
    res = await catalog_sv.find_by_name("my_name")

    assert res == cts

@pytest.mark.asyncio
async def test_embedding_search_empty(catalog_sv: CatalogService):
    ai_intent_booking = AIIntentBooking(
        intent="create_booking",
        catalog_query="",
        search_keywords=[],
    )

    res = await catalog_sv.embedding_search(ai_intent_booking)

    assert res == []
    catalog_sv.em_sv.embed_by_intent.assert_not_awaited()
    catalog_sv.ct_rp.embedding_search.assert_not_awaited()

@pytest.mark.asyncio(
)
async def test_embedding_search_success(catalog_sv: CatalogService):
    catalog_1 = Mock()
    catalog_2 = Mock()
    ai_intent_booking = AIIntentBooking(
        intent="create_booking",
        catalog_query="sa",
        search_keywords=["ds", "saa"],
    )
    catalog_sv.em_sv.embed_by_intent.return_value = [5.5] * 4
    catalog_sv.ct_rp.embedding_search.return_value = [
        (catalog_1, 0.2),
        (catalog_2, 0.7),
    ]
    res = await catalog_sv.embedding_search(ai_intent_booking)

    assert res == [catalog_1]

@pytest.mark.asyncio
async def test_embedding_search_by_name_empty(catalog_sv: CatalogService):

    res = await catalog_sv.embedding_search_by_name("")

    assert res == []
    catalog_sv.em_sv.embed_by_intent.assert_not_awaited()
    catalog_sv.ct_rp.embedding_search.assert_not_awaited()

@pytest.mark.asyncio(
)
async def test_embedding_search_by_name_success(catalog_sv: CatalogService):
    catalog_1 = Mock()
    catalog_2 = Mock()

    catalog_sv.em_sv.embed_by_intent.return_value = [5.5] * 4
    catalog_sv.ct_rp.embedding_search.return_value = [
        (catalog_1, 0.2),
        (catalog_2, 0.7),
    ]
    res = await catalog_sv.embedding_search_by_name("test_input")

    assert res == [catalog_1]