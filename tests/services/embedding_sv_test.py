from unittest import result

from app.service.embedding import EmbeddingService
from unittest.mock import patch, Mock
import pytest

@pytest.fixture
def embedding_sv() -> EmbeddingService:
    model_name = "test-model"
    local_files_only = True

    return EmbeddingService(model_name, local_files_only)

def test_get_model(embedding_sv: EmbeddingService):
    with patch("app.service.embedding.SentenceTransformer") as mock_st:
        model_1 = embedding_sv.get_ml_model()
        model_2 = embedding_sv.get_ml_model()

        mock_st.assert_called_once_with(
            embedding_sv.model_name,
            local_files_only=embedding_sv.local_files_only,
        )

        assert model_1 is mock_st.return_value
        assert model_2 is model_1
        assert embedding_sv.model is model_1

def test_ml_passage(embedding_sv: EmbeddingService):
    test_model = Mock()
    test_vector = Mock()
    embedding_sv.get_ml_model = Mock(return_value=test_model)

    test_model.encode.return_value = test_vector
    test_vector.tolist.return_value = [6.7] * 384

    result = embedding_sv.ml_passage("test_text")

    assert result == [6.7] * 384
    embedding_sv.get_ml_model.assert_called_once()
    test_model.encode.assert_called_once_with(
        "passage: test_text",
        normalize_embeddings=True,
    )
    test_vector.tolist.assert_called_once()

def test_ml_query(embedding_sv: EmbeddingService):
    test_model = Mock()
    test_vector = Mock()
    embedding_sv.get_ml_model = Mock(return_value=test_model)

    test_model.encode.return_value = test_vector
    test_vector.tolist.return_value = [6.7] * 384

    result = embedding_sv.ml_query("test_text")

    assert result == [6.7] * 384
    embedding_sv.get_ml_model.assert_called_once()
    test_model.encode.assert_called_once_with(
        "query: test_text",
        normalize_embeddings=True,
    )
    test_vector.tolist.assert_called_once()