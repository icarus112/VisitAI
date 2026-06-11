import logging
from functools import lru_cache
from sentence_transformers import SentenceTransformer

MODEL_NAME = "intfloat/multilingual-e5-small"
logger = logging.getLogger(__name__)

class MLService:
