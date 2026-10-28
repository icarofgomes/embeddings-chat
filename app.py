import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAIError

from search.chain import ModelError, build_chain, reply
from search.index import load, ready
from search.prompt import SUGGESTIONS

load_dotenv()

st.title("CPNT 2026")

if "messages" not in st.session_state:
    st.session_state.messages = []


@st.cache_resource
def open_index():
    return load()


def answer(question):
    st.session_state.messages.append({"role": "user", "content": question})
    try:
        if not os.getenv("OPENAI_API_KEY"):
            text, hits = "Coloca a OPENAI_API_KEY no .env.", []
        elif not ready():
            text, hits = "Roda python -m search.index antes.", []
        else:
            text, hits = reply(question, open_index(), build_chain())
    except (ModelError, OpenAIError):
        text, hits = "Não consegui responder agora.", []
    st.session_state.messages.append(
        {"role": "assistant", "content": text, "hits": hits}
    )


draft = st.session_state.pop("draft", None)
if draft:
    answer(draft)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        # O mesmo arquivo pode voltar em mais de um bloco. Na tela ele aparece uma vez.
        seen = []
        for hit in message.get("hits") or []:
            source = hit["source"]
            if not source or source in seen:
                continue
            seen.append(source)
        if seen:
            label = "Referência" if len(seen) == 1 else "Referências"
            st.caption(label + ":")
            for source in seen:
                st.caption(source)

if st.session_state.messages:
    if st.button("Limpar"):
        st.session_state.messages = []
        st.rerun()
else:
    st.caption("Sugestões de perguntas")
    for suggestion in SUGGESTIONS:
        if st.button(suggestion):
            st.session_state.draft = suggestion
            st.rerun()

typed = st.chat_input("Pergunte sobre o concurso")
if typed:
    answer(typed)
    st.rerun()
