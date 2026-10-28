import pytest
from langchain_core.documents import Document

from search.chain import ModelError, reply
from search.prompt import MISSING


class FakeChain:
    def __init__(self, result="Em até 5 dias úteis.", error=None):
        self.result = result
        self.error = error
        self.calls = []

    def invoke(self, payload):
        self.calls.append(payload)
        if self.error:
            raise self.error
        return self.result


class FakeStore:
    def __init__(self, pairs):
        self.pairs = pairs
        self.calls = []

    def similarity_search_with_score(self, query, k):
        self.calls.append(query)
        return self.pairs[:k]


def _hit(text, score):
    distance = 2.0 * (1.0 - score)
    return (Document(page_content=text, metadata={"source": "01.md"}), distance)


def test_blank_does_not_search():
    store = FakeStore([_hit("5 dias úteis.", 0.9)])
    chain = FakeChain()

    answer, hits = reply("   ", store, chain)

    assert answer == "Escreve a pergunta."
    assert hits == []
    assert store.calls == []
    assert chain.calls == []


def test_low_score_skips_the_model():
    store = FakeStore([_hit("O edital cita recurso.", 0.1)])
    chain = FakeChain()

    answer, hits = reply("Qual o prazo para entrar com recurso?", store, chain)

    assert answer == MISSING
    assert hits == []
    assert chain.calls == []


def test_chain_receives_only_the_retrieved_text():
    store = FakeStore([_hit("Confirme em 5 dias úteis.", 0.9)])
    chain = FakeChain()

    answer, hits = reply("Quanto tempo tenho?", store, chain)

    assert answer == "Em até 5 dias úteis."
    assert hits[0]["text"] == "Confirme em 5 dias úteis."
    assert chain.calls[0]["context"] == "Confirme em 5 dias úteis."
    assert chain.calls[0]["question"] == "Quanto tempo tenho?"


def test_model_failure():
    store = FakeStore([_hit("Confirme em 5 dias úteis.", 0.9)])
    chain = FakeChain(error=RuntimeError("timeout"))

    with pytest.raises(ModelError):
        reply("Quanto tempo tenho?", store, chain)
