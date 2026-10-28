import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from search.index import search
from search.prompt import HUMAN, MISSING, SYSTEM


class ModelError(Exception):
    pass


def build_chain():
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM),
            ("human", HUMAN),
        ]
    )
    # O id fica na env para trocar o modelo sem mexer aqui.
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(model=model_name, temperature=0)
    return prompt | llm | StrOutputParser()


def reply(question, store, chain):
    text = question.strip()
    if not text:
        return "Escreve a pergunta.", []

    try:
        hits = search(text, store)
        # Sem trecho acima do piso o modelo não entra.
        if not hits:
            return MISSING, []
        context = "\n\n".join(hit["text"] for hit in hits)
        answer = chain.invoke({"context": context, "question": text})
    except Exception as error:
        raise ModelError("Não consegui responder agora.") from error
    return answer, hits
