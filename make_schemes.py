"""Генерация диаграмм архитектур сетей для отчётов всех лабораторных работ.

Запуск: python make_schemes.py
Создаёт PNG-схемы в lab_N/figures/labN_scheme*.png.

Два стиля:
- neuron_graph — графовая схема нейронов (для неглубоких сетей lab_1, lab_2);
- block_diagram — вертикальный стек подписанных блоков (для глубоких сетей lab_3–6).
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent


def neuron_graph(layers: list[int], title: str, path: Path,
                 layer_titles: list[str], input_labels: list[str] | None = None,
                 max_draw: int = 9) -> None:
    """Рисует полносвязную схему нейронов по числу нейронов в слоях."""
    fig, ax = plt.subplots(figsize=(8, 5))
    xs = list(range(len(layers)))
    positions = []
    for li, n in enumerate(layers):
        draw_n = min(n, max_draw)
        ys = [i - (draw_n - 1) / 2 for i in range(draw_n)]
        positions.append(ys)

    # связи между соседними слоями
    for li in range(len(layers) - 1):
        for y0 in positions[li]:
            for y1 in positions[li + 1]:
                ax.plot([xs[li], xs[li + 1]], [y0, y1], color="0.75", lw=0.8, zorder=1)

    # нейроны
    for li, ys in enumerate(positions):
        truncated = layers[li] > len(ys)
        color = "#cfe2ff" if li == 0 else "#ffe0b3" if li < len(layers) - 1 else "#d6f5d6"
        for k, y in enumerate(ys):
            ax.add_patch(plt.Circle((xs[li], y), 0.16, color=color, ec="black", zorder=3))
            if li == 0 and input_labels and k < len(input_labels):
                ax.text(xs[li] - 0.32, y, input_labels[k], ha="right", va="center", fontsize=11)
        if truncated:
            ax.text(xs[li], min(ys) - 0.7, "⋮", ha="center", va="center", fontsize=18)
        ax.text(xs[li], max(positions[li]) + 1.0, layer_titles[li],
                ha="center", va="bottom", fontsize=11, fontweight="bold")

    ax.set_xlim(-1.2, len(layers) - 0.4)
    top = max(max(p) for p in positions) + 1.8
    bottom = min(min(p) for p in positions) - 1.2
    ax.set_ylim(bottom, top)
    ax.set_aspect("equal")  # чтобы нейроны были круглыми, а не вытянутыми
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def block_diagram(blocks: list[str], title: str, path: Path) -> None:
    """Рисует вертикальный стек подписанных блоков со стрелками."""
    n = len(blocks)
    fig, ax = plt.subplots(figsize=(6.4, 0.95 * n + 0.8))
    box_h, box_w, gap = 0.62, 4.6, 0.42
    y = 0.0
    centers = []
    for text in blocks:
        rect = mpatches.FancyBboxPatch(
            (-box_w / 2, y), box_w, box_h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.2, edgecolor="black", facecolor="#eef3fb",
        )
        ax.add_patch(rect)
        ax.text(0, y + box_h / 2, text, ha="center", va="center", fontsize=11)
        centers.append(y + box_h / 2)
        y += box_h + gap

    for i in range(n - 1):
        y_from = centers[i] + box_h / 2
        y_to = centers[i + 1] - box_h / 2
        ax.annotate("", xy=(0, y_to), xytext=(0, y_from),
                    arrowprops=dict(arrowstyle="-|>", color="black", lw=1.2))

    ax.set_xlim(-box_w / 2 - 0.3, box_w / 2 + 0.3)
    ax.set_ylim(-0.4, y + 0.4)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.axis("off")
    plt.tight_layout()
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)


def figdir(lab: int) -> Path:
    d = ROOT / f"lab_{lab}" / "figures"
    d.mkdir(parents=True, exist_ok=True)
    return d


def build() -> None:
    # ---- lab_1: персептрон Розенблатта ----
    d = figdir(1)
    neuron_graph(
        [2, 1], "Персептрон Розенблатта (бинарная классификация)",
        d / "lab1_scheme1.png",
        layer_titles=["Вход (2)", "Нейрон\nhardlim"],
        input_labels=["x1", "x2"],
    )
    neuron_graph(
        [2, 2], "Персептрон с 2 нейронами (классификация на 4 класса)",
        d / "lab1_scheme2.png",
        layer_titles=["Вход (2)", "Слой\n2×hardlim"],
        input_labels=["x1", "x2"],
    )

    # ---- lab_2: многослойные сети ----
    d = figdir(2)
    neuron_graph(
        [2, 20, 3], "MLP для классификации: [2] → [20, tanh] → [3, sigmoid]",
        d / "lab2_scheme1.png",
        layer_titles=["Вход (2)", "Скрытый\n20, tanh", "Выход\n3, sigmoid"],
        input_labels=["x1", "x2"],
    )
    neuron_graph(
        [1, 10, 1], "MLP для аппроксимации: [1] → [10, tanh] → [1, purelin]",
        d / "lab2_scheme2.png",
        layer_titles=["Вход (1)", "Скрытый\n10, tanh", "Выход\n1, purelin"],
        input_labels=["t"],
    )

    # ---- lab_3: Хопфилд и Хэмминг (без Элмана) ----
    d = figdir(3)
    block_diagram(
        ["Вход: образ 12×10 (120)", "Рекуррентный слой Хопфилда\n(весовая матрица 120×120)",
         "600 итераций обновления", "Выход: восстановленный образ (120)"],
        "Схема сети Хопфилда", d / "lab3_scheme1.png",
    )
    block_diagram(
        ["Вход: образ 12×10 (120)", "Слой расстояний Хэмминга\nIW (3×120), a¹ = IW·p + b",
         "Слой конкуренции (poslin)\nрекуррентный, ε = 1/2", "Выход: 3 класса (one-hot)"],
        "Схема сети Хэмминга", d / "lab3_scheme2.png",
    )

    # ---- lab_4: глубокие полносвязные сети ----
    d = figdir(4)
    block_diagram(
        ["Вход: мульти-горячий вектор (5000)", "Dense 16, relu", "Dense 32, relu",
         "Dense 16, tanh", "Dense 1, sigmoid"],
        "Сеть IMDB (вариант 13)", d / "lab4_scheme1.png",
    )
    block_diagram(
        ["Вход: мульти-горячий вектор (10000)", "Dense 32, tanh", "Dense 64, mish",
         "Dense 64, relu", "Dense 46, softmax"],
        "Сеть Reuters (вариант 13)", d / "lab4_scheme2.png",
    )
    block_diagram(
        ["Вход: 13 признаков", "Dense 32, tanh", "Dense 64, mish",
         "Dense 64, relu", "Dense 1 (линейный)"],
        "Сеть Boston Housing (вариант 13)", d / "lab4_scheme3.png",
    )

    # ---- lab_5: свёрточные сети ----
    d = figdir(5)
    block_diagram(
        ["Вход: 1×28×28", "Conv 64 (3×3, relu)", "Conv 128 (3×3, relu) + MaxPool",
         "Conv 128 (3×3, relu)", "Conv 256 (3×3, relu) + MaxPool",
         "Flatten → Dense 512 (relu, dropout)", "Dense 10 (softmax)"],
        "CNN для MNIST (вариант 13)", d / "lab5_scheme1.png",
    )
    block_diagram(
        ["Вход: 1×28×28", "Conv 32 (3×3, relu) + MaxPool",
         "Conv 64 (3×3, relu) + MaxPool", "Flatten → Dense 64 (relu)", "Dense 10 (softmax)"],
        "Базовая CNN для MNIST", d / "lab5_scheme2.png",
    )
    block_diagram(
        ["Вход: 3×224×224", "ResNet18 (свёрточная основа, заморожена)",
         "Dense 256 (relu, dropout 0.5)", "Dense 1 (sigmoid)"],
        "Перенос обучения (Cats vs Dogs)", d / "lab5_scheme3.png",
    )
    block_diagram(
        ["Вход: 3×200×200", "Conv 32 (3×3) + MaxPool", "Conv 64 (3×3) + MaxPool",
         "Conv 64 (3×3) + MaxPool", "Conv 128 (3×3) + MaxPool",
         "Flatten → Dense 256 (relu, dropout)", "Dense 1 (sigmoid)"],
        "CNN для Cats vs Dogs (вариант 13)", d / "lab5_scheme4.png",
    )

    # ---- lab_6: рекуррентные сети ----
    d = figdir(6)
    block_diagram(
        ["Вход: последовательность токенов", "Embedding (64)",
         "BiLSTM 32 (слой 1)", "BiLSTM 32 (слой 2)", "Dense 1 (логит)"],
        "Двунаправленная LSTM для IMDB (вариант 13)", d / "lab6_scheme1.png",
    )
    block_diagram(
        ["Вход: последовательность токенов", "Embedding (64)",
         "Conv1D ×3 (relu)", "Global Max Pooling", "Dense 1 (логит)"],
        "Одномерная свёрточная сеть для IMDB", d / "lab6_scheme2.png",
    )
    block_diagram(
        ["Вход: окно 240×14", "BiLSTM 64 (слой 1)", "BiLSTM 64 (слой 2)",
         "BiLSTM 64 (слой 3)", "Dense 1 (температура)"],
        "Рекуррентная сеть для Jena Climate (вариант 13)", d / "lab6_scheme3.png",
    )
    block_diagram(
        ["Вход: окно 240×14", "Conv1D ×3 (relu)", "LSTM", "Dense 1 (температура)"],
        "Свёрточно-рекуррентная сеть для Jena Climate", d / "lab6_scheme4.png",
    )

    print("Все схемы сгенерированы.")


if __name__ == "__main__":
    build()
