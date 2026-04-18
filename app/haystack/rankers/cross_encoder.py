from haystack.components.rankers import TransformersSimilarityRanker
from app.core.config import settings


def get_ranker(top_k: int = None, model: str = None):
    return TransformersSimilarityRanker(
        model=model or settings.RANKER_MODEL,
        top_k=top_k or settings.RANKER_TOP_K
    )
