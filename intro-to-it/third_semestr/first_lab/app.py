"""Запуск: streamlit run app.py."""

import os
from time import perf_counter

import streamlit as st

from chunking import load_documents, split_documents
from llm import answer_question
from retrival import build_indexes, retrieve

ARTICLE_LIMIT = 500  # Сколько уникальных статей загрузить в базу; None — все.
TOP_K = 10  # Сколько найденных чанков передать LLM.


@st.cache_resource(show_spinner=False)
def prepare_index():
    started = perf_counter()
    documents, stats = load_documents(limit=ARTICLE_LIMIT)
    chunks = split_documents(documents)
    vector_store, bm25 = build_indexes(chunks)
    stats["seconds"] = round(perf_counter() - started, 1)
    return vector_store, bm25, stats, len(chunks)


st.set_page_config(page_title="Хабр · RAG", page_icon="📚", layout="centered")
st.caption("ЛАБОРАТОРНАЯ 01 · LANGCHAIN + FAISS + BM25")
st.title("📚 Спросите у Хабра")
st.write("Ответы по статьям со ссылками на найденные фрагменты.")

with st.sidebar:
    st.header("Подключение")
    api_key = st.text_input("API-ключ DeepSeek", type="password")
    st.caption("Без ключа работает только поиск по статьям.")
    if st.button("Собрать базу знаний", type="primary"):
        try:
            with st.spinner("Очистка статей и индексация. Первый запуск скачает модель VK…"):
                st.session_state["index"] = prepare_index()
        except Exception:
            st.error("Не удалось собрать базу. Проверьте файл данных, память и доступ к Hugging Face.")

if "index" not in st.session_state:
    st.info("Нажмите «Собрать базу знаний» в меню слева.")
    st.stop()

vector_store, bm25, stats, chunk_count = st.session_state["index"]
st.caption(f"База готова: {stats['documents']} статей · {chunk_count} фрагментов · {stats['seconds']} с")

with st.form("question"):
    question = st.text_input("Ваш вопрос", placeholder="Что такое симметрия в программировании?")
    submitted = st.form_submit_button("Найти ответ", type="primary")

if submitted and question.strip():
    try:
        with st.spinner("Ищу фрагменты…"):
            documents = retrieve(question, vector_store, bm25, k=TOP_K)
        if api_key or os.getenv("DEEPSEEK_API_KEY"):
            try:
                with st.spinner("DeepSeek готовит ответ…"):
                    st.markdown(answer_question(question, documents, api_key))
            except Exception:
                st.error("DeepSeek не ответил. Проверьте ключ, баланс и соединение.")
        else:
            st.info("Добавьте ключ DeepSeek для ответа. Найденные фрагменты доступны ниже.")
        st.subheader("Источники")
        for i, doc in enumerate(documents, start=1):
            with st.expander(f"[{i}] {doc.metadata['title']}", expanded=i == 1):
                st.text(doc.page_content)
                if doc.metadata["lead_only"]:
                    st.caption("В выгрузке доступен только анонс статьи.")
                if doc.metadata["source"]:
                    st.link_button("Открыть статью", doc.metadata["source"])
    except ValueError as error:
        st.warning(str(error))
    except Exception:
        st.error("Не удалось выполнить поиск. Попробуйте перезапустить приложение.")
