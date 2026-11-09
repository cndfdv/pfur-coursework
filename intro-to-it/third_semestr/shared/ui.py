"""Общие элементы учебных экранов Streamlit."""

import base64
import os
from pathlib import Path

import streamlit as st

from shared.config import INDEX_DIR
from shared.index import IndexStore


def setup_page(number, title, description):
    st.set_page_config(page_title=f"Лабораторная {number} · RAG", layout="wide")
    fonts = Path(__file__).parent / "assets" / "fonts"
    css = ""
    for family in ("Lora", "Manrope"):
        for subset in ("latin", "cyrillic"):
            encoded = base64.b64encode(
                (fonts / f"{family.lower()}-{subset}.woff2").read_bytes()
            ).decode()
            ranges = "U+0400-052F,U+2116" if subset == "cyrillic" else "U+0000-00FF,U+2000-206F"
            css += f"@font-face{{font-family:{family};src:url(data:font/woff2;base64,{encoded});font-weight:400 700;unicode-range:{ranges};font-display:swap;}}"
    st.markdown(
        f"""<style>{css}
    .stApp {{background:#f6f5f1;color:#202923;font-family:Manrope,sans-serif}}
    [data-testid=stSidebar] {{background:#f2f3ee}}
    .stMainBlockContainer {{max-width:1220px;padding-top:3rem}}
    h1 {{font-family:Lora,serif!important;font-weight:400!important;letter-spacing:-.035em}}
    h2,h3,p,label,input,textarea,button {{font-family:Manrope,sans-serif!important}}
    h2 {{font-size:1.25rem!important}} h3 {{font-size:1.1rem!important}}
    button {{min-height:44px;border-radius:9px!important}}
    button[kind=primary] {{background:#126b3c;color:white;border-color:#126b3c}}
    a {{color:#126b3c}} [data-testid=stExpander] {{background:white;border-radius:12px}}
    :focus-visible {{outline:2px solid #126b3c!important;outline-offset:3px}}
    @media(max-width:720px) {{.stMainBlockContainer{{padding:2rem 1rem}} input,textarea{{font-size:16px!important}}}}
    </style>""",
        unsafe_allow_html=True,
    )
    st.caption(f"ПРАКТИКУМ ПО ПРОГРАММИРОВАНИЮ · ЛАБОРАТОРНАЯ {number}")
    st.title(title)
    st.write(description)


def sidebar():
    with st.sidebar:
        st.subheader("Подключение")
        key = st.text_input("API-ключ OpenAI", type="password") or os.getenv("OPENAI_API_KEY")
        st.caption("GPT-6 Luna · medium effort. Без ключа доступен поиск и разбор шагов.")
        st.divider()
        st.caption(
            "Источники: Хабр, научные статьи и новости. По 10 000 документов в каждом индексе."
        )
    return key


@st.cache_resource(show_spinner="Загрузка индексов…")
def load_indexes():
    try:
        return {source: IndexStore(INDEX_DIR / source) for source in ("habr", "science", "news")}
    except FileNotFoundError:
        st.error("Данные ещё не подготовлены. Выполните `python -m scripts.build_indexes` на home.")
        st.stop()
    except RuntimeError as error:
        st.error(f"Не удалось прочитать FAISS-индекс: {error}")
        st.stop()


def show_result(result):
    st.subheader("Ответ")
    st.write(result["answer"])
    for warning in dict.fromkeys(result.get("warnings", [])):
        st.warning(warning)
    left, right = st.columns([1, 2])
    with left:
        st.subheader("Шаги решения")
        for number, step in enumerate(result["steps"], 1):
            st.write(f"{number}. {step}")
    with right:
        st.subheader("Источники")
        for number, document in enumerate(result.get("documents", []), 1):
            with st.expander(f"[{number}] {document.title} · {document.score:.2f}"):
                st.text(document.text)
                if document.url.startswith(("https://", "http://")):
                    st.link_button("Открыть источник", document.url)
