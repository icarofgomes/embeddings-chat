# CPNT 2026

Os posts em `data/` são fictícios. Eu gerei esse material no ChatGPT.

Chat para perguntar sobre o concurso. A busca acha os trechos e o modelo responde só com eles.

## Rodar

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Preencha `OPENAI_API_KEY` no `.env`.

```bash
python -m search.index
streamlit run app.py
```

Testes: `pytest`

## Busca

Os cinco posts são cortados em blocos de 1000 caracteres, com 200 de sobreposição. O bloco seguinte recomeça 200 caracteres antes do fim do anterior. A frase que cairia na divisa continua inteira num dos dois.

Cada bloco vira um vetor com `text-embedding-3-small` e fica num FAISS em `store/`. A pergunta usa o mesmo modelo. A nota é o cosseno: maior é mais parecido. Abaixo de 0,56 a lista volta vazia e o modelo não é chamado.

## Exemplos

Com a conversa vazia, a tela oferece três perguntas. Embaixo da resposta fica "Referência" e o nome do arquivo. Mais de um arquivo vira "Referências". Limpar zera a conversa e devolve as sugestões.

Quanto tempo tenho para confirmar a vaga depois da convocação?

A busca devolve `01_prazo_matricula.md`. A resposta: até 5 dias úteis após a publicação da convocação oficial. A pergunta fala em tempo. O post fala em 5 dias úteis.

A nota da recuperação substitui a anterior no módulo?

A busca devolve o trecho de `03_recuperacao.md` em que a nota da recuperação entra no lugar da anterior, para a aprovação no módulo.

Qual o prazo para entrar com recurso?

O material cita recurso e não informa o prazo. A nota ficou em 0,55, abaixo do corte. A resposta sai sem chamar o modelo: Não encontrei essa informação no material.

## Decisões

O embedding é o `text-embedding-3-small`. A dica da prova cita transformers. Fiquei na OpenAI porque a questão anterior já usa a mesma chave.

O índice é FAISS, gravado em disco. Milvus pediria um serviço a mais para cinco posts.

`python -m search.index` reconstrói o índice quando o texto muda. A pergunta não refaz o embedding dos posts.

Abaixo de 0,56 o modelo não entra. A frase de recusa sai direto.

Cada pergunta busca de novo. O histórico não vai junto.

O id do modelo de resposta está em `OPENAI_MODEL`. O padrão é `gpt-4o-mini`. O de embedding está em `OPENAI_EMBEDDING_MODEL`.

LangSmith liga com `LANGSMITH_TRACING=true` e `LANGSMITH_API_KEY`. Sem a chave, o chat funciona igual. O projeto do trace é `embeddings-chat`.

Sem login. O enunciado não pede.
