from haystack.components.rankers import TransformersSimilarityRanker


def get_ranker(top_k: int = 5, model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
    return TransformersSimilarityRanker(model=model, top_k=top_k)
