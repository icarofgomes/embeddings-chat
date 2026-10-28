from pathlib import Path

from streamlit.testing.v1 import AppTest

from search.prompt import SUGGESTIONS

APP = Path(__file__).resolve().parents[1] / "app.py"


def _app(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    return AppTest.from_file(APP, default_timeout=15).run()


def test_screen_shows_three_questions(monkeypatch):
    app = _app(monkeypatch)

    assert [button.label for button in app.button] == list(SUGGESTIONS)


def test_suggestion_asks_for_the_key(monkeypatch):
    app = _app(monkeypatch)

    app.button[0].click().run()

    assert app.chat_message[0].markdown[0].value == SUGGESTIONS[0]
    assert app.chat_message[1].markdown[0].value == "Coloca a OPENAI_API_KEY no .env."
    assert [button.label for button in app.button] == ["Limpar"]


def test_clear_brings_the_suggestions_back(monkeypatch):
    app = _app(monkeypatch)

    app.button[0].click().run()
    app.button[0].click().run()

    assert app.chat_message == []
    assert [button.label for button in app.button] == list(SUGGESTIONS)


def test_typed_question_asks_for_the_key(monkeypatch):
    app = _app(monkeypatch)

    app.chat_input[0].set_value("Qual o prazo para entrar com recurso?").run()

    assert app.chat_message[0].markdown[0].value == "Qual o prazo para entrar com recurso?"
    assert app.chat_message[1].markdown[0].value == "Coloca a OPENAI_API_KEY no .env."
