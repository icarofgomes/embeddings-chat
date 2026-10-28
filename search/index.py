import os
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
STORE = ROOT / "store"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
# Cosseno, maior é mais parecido. Nestes posts a convocação fica em 0,57 e o recurso em 0,55.
FLOOR = 0.56


def embeddings():
    # O id fica na env para trocar o modelo sem mexer aqui.
    model_name = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    return OpenAIEmbeddings(model=model_name)


def load_posts():
    docs = []
    for path in sorted(DATA.glob("*.md")):
        docs.append(
            Document(
                page_content=path.read_text(encoding="utf-8"),
                metadata={"source": path.name},
            )
        )
    return docs


def split(docs):
    # O bloco seguinte recomeça 200 caracteres antes. A frase na divisa não se perde.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(docs)


def build(embedder=None):
    embedder = embedder or embeddings()
    store = FAISS.from_documents(split(load_posts()), embedder)
    STORE.mkdir(parents=True, exist_ok=True)
    store.save_local(str(STORE))
    return store


def ready():
    return (STORE / "index.faiss").exists()


def load(embedder=None):
    embedder = embedder or embeddings()
    # O índice foi gerado aqui. O load pede essa flag para abrir o arquivo local.
    return FAISS.load_local(
        str(STORE),
        embedder,
        allow_dangerous_deserialization=True,
    )


def search(query, store, k=3, floor=FLOOR):
    text = query.strip()
    if not text:
        return []

    # FAISS devolve a distância ao quadrado. Em vetor normalizado, 1 - d/2 é o cosseno.
    found = store.similarity_search_with_score(text, k=k)
    hits = []
    for doc, distance in found:
        score = 1.0 - float(distance) / 2.0
        if score < floor:
            continue
        hits.append(
            {
                "source": doc.metadata.get("source", ""),
                "text": doc.page_content,
                "score": score,
            }
        )
    return hits


def main():
    from dotenv import load_dotenv

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("Coloca a OPENAI_API_KEY no .env.")
    store = build()
    print(f"{store.index.ntotal} blocos em store/")


if __name__ == "__main__":
    main()
