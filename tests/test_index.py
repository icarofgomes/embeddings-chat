from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from search.index import FLOOR, load_posts, search, split


class Fixed(Embeddings):
    def __init__(self, vectors):
        self.vectors = vectors

    def embed_documents(self, texts):
        return [list(self.vectors[text]) for text in texts]

    def embed_query(self, text):
        return list(self.vectors[text])


VECTORS = {
    "prazo de cinco dias": [1.0, 0.0, 0.0],
    "certificado em dez dias": [0.0, 1.0, 0.0],
    "canal de atendimento": [0.0, 0.0, 1.0],
}


def _store():
    from langchain_community.vectorstores import FAISS

    docs = [
        Document(page_content=text, metadata={"source": f"{text}.md"})
        for text in VECTORS
    ]
    return FAISS.from_documents(docs, Fixed(VECTORS))


def test_posts_split_into_more_than_one_block():
    chunks = split(load_posts())
    counts = {}
    for chunk in chunks:
        source = chunk.metadata["source"]
        counts[source] = counts.get(source, 0) + 1

    assert len(counts) == 5
    assert all(count > 1 for count in counts.values())


def test_nearest_chunk_comes_first():
    hits = search("prazo de cinco dias", _store(), floor=0)

    assert hits[0]["source"] == "prazo de cinco dias.md"
    assert hits[0]["text"] == "prazo de cinco dias"


def test_k_limits_the_list():
    hits = search("prazo de cinco dias", _store(), k=1, floor=0)

    assert len(hits) == 1


def test_below_floor_returns_empty():
    hits = search("prazo de cinco dias", _store(), floor=FLOOR + 1)

    assert hits == []
