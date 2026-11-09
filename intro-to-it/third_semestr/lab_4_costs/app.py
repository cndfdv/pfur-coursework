"""Запуск из корня: streamlit run lab_4_costs/app.py."""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lab_4_costs.logic import run_question
from shared.costs import show_dashboard
from shared.ui import load_indexes, setup_page, show_result, sidebar

setup_page(4, "Стоимость RAG", "Опечатки, составные вопросы и стоимость каждого этапа графа.")
api_key = sidebar()
try:
    indexes = load_indexes()
except (FileNotFoundError, RuntimeError) as error:
    st.error(f"Не удалось загрузить индексы ({type(error).__name__}).")
    st.info("Сначала выполните python -m scripts.build_indexes из корня проекта.")
    st.stop()

st.session_state.setdefault("lab4_cost_rows", [])
st.session_state.setdefault("lab4_last", None)
question = st.text_area("Вопрос", "Что такое машинное обучение и как его применяют?")
if st.button("Выполнить", type="primary", disabled=not question.strip()):
    try:
        with st.spinner("Обрабатываем вопрос…"):
            results, rows, corrected, subquestions = run_question(question, indexes, api_key)
        st.session_state.lab4_cost_rows.extend(rows)
        st.session_state.lab4_last = (question, corrected, subquestions, results)
    except Exception as error:
        st.error(f"Запрос не выполнен ({type(error).__name__}). Проверьте настройки и доступность API.")

if st.session_state.lab4_last:
    original, corrected, subquestions, results = st.session_state.lab4_last
    st.write("Исходный вопрос:", original)
    st.write("После исправления:", corrected)
    for number, (subquestion, result) in enumerate(zip(subquestions, results), 1):
        st.subheader(f"Подзапрос {number}: {subquestion}")
        show_result(result)

st.subheader("Cost Dashboard")
st.caption("История успешных запросов сохраняется в текущей сессии браузера.")
if st.button("Очистить историю стоимости"):
    st.session_state.lab4_cost_rows = []
if st.session_state.lab4_cost_rows:
    show_dashboard(st.session_state.lab4_cost_rows)
else:
    st.info("Выполните вопрос, чтобы увидеть измерения.")
