"""Общий генератор отчётов по лабораторным работам.

Формат повторяет отчёты к работам №1 и №2: лист формата A4, шрифт 14 pt,
межстрочный интервал 1.15, титульный лист, разделы «Цель работы»,
«Основные этапы работы», «Сценарий выполнения работы», «Код программы»
и «Вывод». Графики в документе помечаются заглушкой [ВСТАВИТЬ РИСУНОК];
вместо неё нужно вставить скриншоты из ноутбука main.ipynb.

Каждая работа описывает своё содержимое в файле generate_report.py и
вызывает build_report(...). Создаются report_labN.docx и report_labN.pdf.
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Emu, Pt
from PIL import Image, ImageDraw, ImageFont

# Регистрируем все кодеки PIL (иначе сохранение PDF не находит JPEG-обработчик).
Image.init()

# Шрифты macOS с поддержкой кириллицы (для растрового PDF).
REG_FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD_FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
MONO_FONT = "/System/Library/Fonts/Supplemental/Courier New.ttf"


# ---------------------------------------------------------------------------
# Конструкторы блоков содержимого. Из этих блоков формируется тело отчёта,
# одинаково отрисовываемое и в docx, и в pdf.
# ---------------------------------------------------------------------------
def heading(text: str) -> tuple:
    return ("h", text)


def para(text: str) -> tuple:
    return ("p", text)


def bold(text: str) -> tuple:
    return ("b", text)


def table(caption: str, headers: list[str], rows: list[list]) -> tuple:
    return ("table", caption, headers, rows)


def figure(caption: str, image: str | None = None) -> tuple:
    return ("fig", caption, image)


def page_break() -> tuple:
    return ("pb",)


# ---------------------------------------------------------------------------
# Чтение кода из ноутбука
# ---------------------------------------------------------------------------
def notebook_code(path: Path) -> list[str]:
    nb = json.loads(path.read_text(encoding="utf-8"))
    chunks: list[str] = []
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
        if source.strip():
            chunks.append(source.strip())
    return chunks


# ---------------------------------------------------------------------------
# DOCX
# ---------------------------------------------------------------------------
def _doc_setup() -> Document:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Emu(914400)
    section.bottom_margin = Emu(914400)
    section.left_margin = Emu(1143000)
    section.right_margin = Emu(1143000)
    style = doc.styles["Normal"]
    style.font.size = Pt(14)
    style.paragraph_format.space_after = Pt(0)
    style.paragraph_format.space_before = Pt(0)
    style.paragraph_format.line_spacing = 1.15
    return doc


def _centered(doc: Document, text: str, bold_text: bool = False) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.font.size = Pt(14)
    run.bold = bold_text


def _normal(doc: Document, text: str, bold_text: bool = False) -> None:
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(14)
    run.bold = bold_text


def _mixed(doc: Document, parts: list[tuple[str, bool]]) -> None:
    p = doc.add_paragraph()
    for text, bold_text in parts:
        run = p.add_run(text)
        run.font.size = Pt(14)
        run.bold = bold_text


def _code(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(10)
    run.font.name = "Courier New"


def _empty(doc: Document, n: int = 1) -> None:
    for _ in range(n):
        doc.add_paragraph()


def _figure_docx(doc: Document, caption: str, image: str | None, folder: Path) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    image_path = (folder / image) if image else None
    if image_path and image_path.exists():
        p.add_run().add_picture(str(image_path), width=Cm(15))
    else:
        run = p.add_run("[ВСТАВИТЬ РИСУНОК]")
        run.font.size = Pt(12)
        run.italic = True
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap_run = cap.add_run(caption)
    cap_run.font.size = Pt(12)


def _table(doc: Document, headers: list[str], rows: list[list]) -> None:
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    for i, header in enumerate(headers):
        t.rows[0].cells[i].text = str(header)
    for r, row in enumerate(rows, start=1):
        for c, value in enumerate(row):
            t.rows[r].cells[c].text = str(value)


def _title_page(doc: Document, number: int, title: str, variant: str) -> None:
    _centered(doc, "ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ ОБРАЗОВАТЕЛЬНОЕ")
    _centered(doc, "УЧРЕЖДЕНИЕ ВЫСШЕГО ОБРАЗОВАНИЯ")
    _centered(doc, "РОССИЙСКИЙ УНИВЕРСИТЕТ ДРУЖБЫ НАРОДОВ")
    _centered(doc, "ИМЕНИ ПАТРИСА ЛУМУМБЫ")
    _empty(doc, 8)
    _centered(doc, "Отчет")
    _centered(doc, f"о выполнении лабораторной работы № {number}")
    _centered(doc, f'"{title}"')
    _centered(doc, 'по дисциплине "Нейронные сети"')
    _empty(doc)
    _centered(doc, f"Вариант задания № {variant}")
    _empty(doc, 3)
    _normal(doc, "Выполнил студент группы ЗФИбд-01-24")
    _normal(doc, "Князев А. М. __________")
    _empty(doc)
    _normal(doc, "Проверил и принял")
    _normal(doc, "Леонов С. С. __________")
    _empty(doc)
    _normal(doc, "с оценкой __________")
    _empty(doc, 4)
    _centered(doc, "Москва, 2026")
    doc.add_page_break()


def _render_blocks_docx(doc: Document, blocks: list[tuple], folder: Path) -> None:
    for block in blocks:
        kind = block[0]
        if kind == "h":
            _normal(doc, block[1], bold_text=True)
            _empty(doc)
        elif kind == "p":
            _normal(doc, block[1])
            _empty(doc)
        elif kind == "b":
            _normal(doc, block[1], bold_text=True)
        elif kind == "table":
            _normal(doc, block[1])
            _table(doc, block[2], block[3])
            _empty(doc)
        elif kind == "fig":
            _figure_docx(doc, block[1], block[2], folder)
            _empty(doc)
        elif kind == "pb":
            doc.add_page_break()


def _build_docx(out: Path, number: int, title: str, variant: str, goal: str,
                stages: list[str], equipment: str, blocks: list[tuple],
                conclusion: list[str], notebook: Path) -> None:
    doc = _doc_setup()
    _title_page(doc, number, title, variant)

    _mixed(doc, [("Цель работы: ", True), (goal, False)])
    _empty(doc)
    _normal(doc, "Основные этапы работы:", bold_text=True)
    for i, stage in enumerate(stages, start=1):
        _normal(doc, f"{i}. {stage}")
    _empty(doc)
    _mixed(doc, [("Программное обеспечение: ", True), (equipment, False)])
    _empty(doc)
    _normal(doc, "Сценарий выполнения работы", bold_text=True)
    _empty(doc)

    _render_blocks_docx(doc, blocks, notebook.parent)

    doc.add_page_break()
    _normal(doc, "Код программы", bold_text=True)
    _empty(doc)
    for chunk in notebook_code(notebook):
        for line in chunk.splitlines():
            _code(doc, line)
        _empty(doc)

    doc.add_page_break()
    _normal(doc, "Вывод", bold_text=True)
    _empty(doc)
    for paragraph in conclusion:
        _normal(doc, paragraph)
        _empty(doc)

    doc.save(out)


# ---------------------------------------------------------------------------
# PDF (растровый, как в исходных генераторах)
# ---------------------------------------------------------------------------
class _PdfBuilder:
    def __init__(self, out: Path):
        self.out = out
        self.pages: list[Image.Image] = []
        self.width = 1240
        self.height = 1754
        self.margin = 90
        self.font = ImageFont.truetype(REG_FONT, 28)
        self.small = ImageFont.truetype(REG_FONT, 22)
        self.bold = ImageFont.truetype(BOLD_FONT, 30)
        self.mono = ImageFont.truetype(MONO_FONT, 17)
        self.new_page()

    def new_page(self) -> None:
        page = Image.new("RGB", (self.width, self.height), "white")
        self.pages.append(page)
        self.draw = ImageDraw.Draw(page)
        self.y = self.margin

    def _ensure(self, amount: int) -> None:
        if self.y + amount > self.height - self.margin:
            self.new_page()

    def line(self, text: str = "", bold: bool = False, mono: bool = False) -> None:
        font = self.mono if mono else self.bold if bold else self.font
        width = 118 if mono else 74
        for wrapped in textwrap.wrap(text, width=width) or [""]:
            self._ensure(40)
            self.draw.text((self.margin, self.y), wrapped, fill="black", font=font)
            self.y += 26 if mono else 40
        self.y += 6

    def center(self, text: str, font=None) -> None:
        font = font or self.bold
        self._ensure(50)
        box = self.draw.textbbox((0, 0), text, font=font)
        x = (self.width - (box[2] - box[0])) // 2
        self.draw.text((x, self.y), text, fill="black", font=font)
        self.y += 50

    def image(self, path: Path, caption: str) -> None:
        if not path.exists():
            self.center("[ВСТАВИТЬ РИСУНОК]", font=self.small)
            self.line(caption)
            return
        img = Image.open(path).convert("RGB")
        max_w = self.width - 2 * self.margin
        img.thumbnail((max_w, 560))
        self._ensure(img.height + 70)
        x = (self.width - img.width) // 2
        self.pages[-1].paste(img, (x, self.y))
        self.y += img.height + 14
        self.line(caption)

    def save(self) -> None:
        first, *rest = self.pages
        first.save(self.out, save_all=True, append_images=rest)


def _build_pdf(out: Path, number: int, title: str, variant: str, goal: str,
               stages: list[str], equipment: str, blocks: list[tuple],
               conclusion: list[str], notebook: Path) -> None:
    pdf = _PdfBuilder(out)
    pdf.y += 80
    pdf.center("Отчет")
    pdf.center(f"о выполнении лабораторной работы № {number}")
    for part in textwrap.wrap(title, width=46):
        pdf.center(part)
    pdf.center(f"Вариант задания № {variant}")
    pdf.y += 120
    pdf.line("Выполнил студент группы ЗФИбд-01-24: Князев А. М.")
    pdf.line("Проверил и принял: Леонов С. С.")
    pdf.y += 60
    pdf.center("Москва, 2026")
    pdf.new_page()

    pdf.line("Цель работы", bold=True)
    pdf.line(goal)
    pdf.line("Основные этапы работы", bold=True)
    for i, stage in enumerate(stages, start=1):
        pdf.line(f"{i}. {stage}")
    pdf.line()
    pdf.line(f"Программное обеспечение: {equipment}")
    pdf.line()
    pdf.line("Сценарий выполнения работы", bold=True)

    for block in blocks:
        kind = block[0]
        if kind == "h":
            pdf.line(block[1], bold=True)
        elif kind == "p":
            pdf.line(block[1])
        elif kind == "b":
            pdf.line(block[1], bold=True)
        elif kind == "table":
            pdf.line(block[1])
            pdf.line(" | ".join(str(x) for x in block[2]))
            for row in block[3]:
                pdf.line(" | ".join(str(x) for x in row))
            pdf.line()
        elif kind == "fig":
            image_path = (notebook.parent / block[2]) if block[2] else None
            pdf.image(image_path if image_path else Path("/nonexistent"), block[1])
        elif kind == "pb":
            pdf.line()

    pdf.new_page()
    pdf.line("Вывод", bold=True)
    for paragraph in conclusion:
        pdf.line(paragraph)

    pdf.new_page()
    pdf.line("Фрагменты кода из main.ipynb", bold=True)
    for chunk in notebook_code(notebook):
        for code_line in chunk.splitlines():
            pdf.line(code_line[:118], mono=True)
        pdf.line()
    pdf.save()


# ---------------------------------------------------------------------------
# Точка входа
# ---------------------------------------------------------------------------
def build_report(*, number: int, title: str, variant: str, goal: str,
                 stages: list[str], equipment: str, blocks: list[tuple],
                 conclusion: list[str], folder: Path) -> None:
    notebook = folder / "main.ipynb"
    docx_path = folder / f"report_lab{number}.docx"
    pdf_path = folder / f"report_lab{number}.pdf"
    _build_docx(docx_path, number, title, variant, goal, stages, equipment,
                blocks, conclusion, notebook)
    _build_pdf(pdf_path, number, title, variant, goal, stages, equipment,
               blocks, conclusion, notebook)
    print(f"created {docx_path.name}")
    print(f"created {pdf_path.name}")
