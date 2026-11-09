"""Фактические токены API и время узлов графа; цены в shared/config.py."""

from time import perf_counter

import pandas as pd
import streamlit as st

from shared.config import CACHED_USD_PER_MILLION, INPUT_USD_PER_MILLION, OUTPUT_USD_PER_MILLION


def token_cost(input_tokens=0, output_tokens=0, cached_tokens=0):
    return (
        (input_tokens - cached_tokens) * INPUT_USD_PER_MILLION
        + cached_tokens * CACHED_USD_PER_MILLION
        + output_tokens * OUTPUT_USD_PER_MILLION
    ) / 1_000_000


def run_graph(graph, question, request_id):
    result, rows = {"question": question}, []
    started = perf_counter()
    for event in graph.stream(result, stream_mode="updates"):
        for stage, update in event.items():
            seconds = perf_counter() - started
            result.update(update)
            usage = update.get("usage", {})
            rows.append(
                {
                    "request": request_id,
                    "stage": stage,
                    "seconds": round(seconds, 4),
                    "input_tokens": usage.get("input_tokens", 0),
                    "output_tokens": usage.get("output_tokens", 0),
                    "cached_tokens": usage.get("cached_tokens", 0),
                    "cost_usd": token_cost(**usage),
                }
            )
            started = perf_counter()
    return result, rows


def show_dashboard(rows):
    st.caption("GPT-6 Luna · Standard API · USD. Reasoning-токены включены в output.")
    if not rows:
        st.info("Выполните запрос: здесь появятся время и стоимость его этапов.")
        return
    frame = pd.DataFrame(rows)
    left, middle, right = st.columns(3)
    left.metric("Запросов в серии", frame["request"].nunique())
    middle.metric("Стоимость серии", f"${frame.cost_usd.sum():.6f}")
    right.metric("Время серии", f"{frame.seconds.sum():.2f} с")
    st.subheader("По запросам")
    st.dataframe(frame.groupby("request", sort=False).sum(numeric_only=True), width="stretch")
    st.subheader("Каждый этап")
    st.dataframe(frame, hide_index=True, width="stretch")
    st.download_button("Скачать CSV", frame.to_csv(index=False), "costs.csv", "text/csv")
    st.caption(
        "Локальный поиск и обработка имеют нулевую цену API. Электроэнергия GPU и интернет не учтены. Без ключа токены и цена равны нулю."
    )
