"""Запуск: streamlit run lab_3_langgraph/app.py."""

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from lab_3_langgraph.graph import GRAPH_DOT, build_graph
from shared.ui import load_indexes, setup_page, show_result, sidebar

setup_page(
    3,
    "Поиск с маршрутизацией",
    "Граф выбирает источник, проверяет ответ и при необходимости повторяет поиск.",
)
api_key = sidebar()
indexes = load_indexes()
with st.expander("Как устроен граф"):
    st.graphviz_chart(GRAPH_DOT)

with st.form("question"):
    question = st.text_input(
        "Ваш вопрос", "Какие научные исследования посвящены машинному обучению?"
    )
    submitted = st.form_submit_button("Найти ответ", type="primary")
if submitted and question.strip():
    try:
        with st.spinner("Граф выполняет запрос…"):
            result = build_graph(indexes, api_key).invoke({"question": question})
        show_result(result)
    except Exception as error:
        st.error(
            f"Не удалось выполнить запрос ({type(error).__name__}). Проверьте соединение, доступ к модели и баланс API."
        )
