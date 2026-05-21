from __future__ import annotations

import json
import textwrap
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Emu, Pt
from PIL import Image, ImageDraw, ImageFont


FOLDER = Path(__file__).resolve().parent
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


LAB_NUMBER = 5
SPEC = {'folder': 'lab_5', 'title': 'Сверточные нейронные сети', 'variant': '13', 'goal': 'изучение сверточных нейронных сетей для распознавания изображений, а также подготовка модели переноса обучения.', 'stages': ['Построить CNN для MNIST.', 'Построить архитектуру CNN для Cats vs Dogs.', 'Подготовить transfer learning модель с замороженной сверточной основой.'], 'tables': [('Таблица 1 — Архитектуры варианта', ['Этап', 'Параметры'], [['MNIST', 'Conv: 64-128-128-256, kernel 3x3, classifier 512'], ['Cats vs Dogs', 'input 200x200, Conv: 32-64-64-128, classifier 256'], ['Transfer learning', 'замороженная основа ResNet18, обучается только классификатор']]), ('Таблица 2 — Результаты', ['Показатель', 'Значение'], [['Устройство', 'cuda'], ['MNIST test_loss', '0.0511'], ['MNIST test_acc', '0.9915'], ['Параметры Cats vs Dogs модели', '4 849 281'], ['Обучаемые параметры transfer-модели', '131 585']])], 'images': [('mnist_history.png', 'Рис. 1 — Графики loss и accuracy для MNIST')], 'conclusion': 'Сверточная сеть варианта 13 достигла высокой точности на MNIST. Для Cats vs Dogs подготовлена требуемая архитектура, а для переноса обучения создана модель с замороженной основой и новым бинарным классификатором.'}


def add_centered(doc: Document, text: str, bold: bool = False) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.size = Pt(14)
    r.bold = bold


def add_paragraph(doc: Document, text: str, bold: bool = False) -> None:
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(14)
    r.bold = bold


def add_code(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.font.size = Pt(9)
    r.font.name = "Courier New"


def add_table(doc: Document, headers: list[str], rows: list[list[str]]) -> None:
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    for i, header in enumerate(headers):
        table.rows[0].cells[i].text = header
    for row_index, row in enumerate(rows, start=1):
        for col_index, value in enumerate(row):
            table.rows[row_index].cells[col_index].text = str(value)


def notebook_code(path: Path) -> list[str]:
    nb = json.loads(path.read_text(encoding="utf-8"))
    chunks: list[str] = []
    for cell in nb["cells"]:
        if cell["cell_type"] != "code":
            continue
        source = "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
        source = source.strip()
        if source:
            chunks.append(source)
    return chunks


def setup_doc() -> Document:
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


def build_docx(number: int, spec: dict) -> Path:
    folder = FOLDER
    doc = setup_doc()

    add_centered(doc, "ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ ОБРАЗОВАТЕЛЬНОЕ")
    add_centered(doc, "УЧРЕЖДЕНИЕ ВЫСШЕГО ОБРАЗОВАНИЯ")
    add_centered(doc, "РОССИЙСКИЙ УНИВЕРСИТЕТ ДРУЖБЫ НАРОДОВ")
    add_centered(doc, "ИМЕНИ ПАТРИСА ЛУМУМБЫ")
    for _ in range(7):
        doc.add_paragraph()
    add_centered(doc, "Отчет", True)
    add_centered(doc, f"о выполнении лабораторной работы № {number}", True)
    add_centered(doc, f'"{spec["title"]}"')
    add_centered(doc, 'по дисциплине "Нейронные сети"')
    doc.add_paragraph()
    add_centered(doc, f'Вариант задания № {spec["variant"]}')
    for _ in range(3):
        doc.add_paragraph()
    add_paragraph(doc, "Выполнил студент группы ЗФИбд-01-24")
    add_paragraph(doc, "Князев А. М. __________")
    doc.add_paragraph()
    add_paragraph(doc, "Проверил и принял")
    add_paragraph(doc, "Леонов С. С. __________")
    doc.add_paragraph()
    add_paragraph(doc, "с оценкой __________")
    for _ in range(4):
        doc.add_paragraph()
    add_centered(doc, "Москва, 2026")
    doc.add_page_break()

    add_paragraph(doc, "Цель работы", True)
    add_paragraph(doc, spec["goal"])
    doc.add_paragraph()
    add_paragraph(doc, "Основные этапы работы", True)
    for index, stage in enumerate(spec["stages"], start=1):
        add_paragraph(doc, f"{index}. {stage}")
    doc.add_paragraph()
    add_paragraph(
        doc,
        "Оборудование и программное обеспечение: персональный компьютер, Python 3, "
        "Jupyter Notebook, PyTorch, NumPy, Matplotlib.",
    )
    doc.add_paragraph()

    add_paragraph(doc, "Ход выполнения работы", True)
    add_paragraph(
        doc,
        "Все расчеты выполнены в файле main.ipynb. В коде используется автоматический "
        "выбор устройства: если CUDA доступна, вычисления выполняются на GPU, иначе на CPU.",
    )
    doc.add_paragraph()

    for caption, headers, rows in spec["tables"]:
        add_paragraph(doc, caption, True)
        add_table(doc, headers, rows)
        doc.add_paragraph()

    for image_name, caption in spec["images"]:
        image_path = folder / image_name
        if image_path.exists():
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(str(image_path), width=Cm(15))
            add_paragraph(doc, caption)
            doc.add_paragraph()

    doc.add_page_break()
    add_paragraph(doc, "Код программы", True)
    for chunk in notebook_code(folder / "main.ipynb"):
        for line in chunk.splitlines():
            add_code(doc, line)
        doc.add_paragraph()

    doc.add_page_break()
    add_paragraph(doc, "Вывод", True)
    add_paragraph(doc, spec["conclusion"])

    out = folder / f"report_lab{number}.docx"
    doc.save(out)
    return out


class PdfBuilder:
    def __init__(self, out: Path):
        self.out = out
        self.pages: list[Image.Image] = []
        self.width = 1240
        self.height = 1754
        self.margin = 90
        self.y = self.margin
        self.font = ImageFont.truetype(FONT, 30)
        self.small = ImageFont.truetype(FONT, 24)
        self.bold = ImageFont.truetype(BOLD_FONT, 34)
        self.mono = ImageFont.truetype(MONO_FONT, 18)
        self.new_page()

    def new_page(self) -> None:
        page = Image.new("RGB", (self.width, self.height), "white")
        self.pages.append(page)
        self.draw = ImageDraw.Draw(page)
        self.y = self.margin

    def ensure(self, amount: int) -> None:
        if self.y + amount > self.height - self.margin:
            self.new_page()

    def line(self, text: str = "", bold: bool = False, mono: bool = False) -> None:
        font = self.mono if mono else self.bold if bold else self.font
        max_chars = 112 if mono else 72
        for wrapped in textwrap.wrap(text, width=max_chars) or [""]:
            self.ensure(42)
            self.draw.text((self.margin, self.y), wrapped, fill="black", font=font)
            self.y += 42 if not mono else 28
        self.y += 8

    def title_center(self, text: str, font=None) -> None:
        font = font or self.bold
        self.ensure(50)
        box = self.draw.textbbox((0, 0), text, font=font)
        x = (self.width - (box[2] - box[0])) // 2
        self.draw.text((x, self.y), text, fill="black", font=font)
        self.y += 52

    def image(self, path: Path, caption: str) -> None:
        if not path.exists():
            return
        img = Image.open(path).convert("RGB")
        max_w = self.width - 2 * self.margin
        max_h = 520
        img.thumbnail((max_w, max_h))
        self.ensure(img.height + 95)
        x = (self.width - img.width) // 2
        self.pages[-1].paste(img, (x, self.y))
        self.y += img.height + 18
        self.line(caption)

    def save(self) -> None:
        first, *rest = self.pages
        first.save(self.out, save_all=True, append_images=rest)


def build_pdf(number: int, spec: dict) -> Path:
    folder = FOLDER
    out = folder / f"report_lab{number}.pdf"
    pdf = PdfBuilder(out)
    pdf.title_center("Отчет")
    pdf.title_center(f"о выполнении лабораторной работы № {number}")
    pdf.title_center(spec["title"])
    pdf.title_center(f"Вариант {spec['variant']}")
    pdf.y += 120
    pdf.line("Выполнил студент группы ЗФИбд-01-24: Князев А. М.")
    pdf.line("Проверил: Леонов С. С.")
    pdf.title_center("Москва, 2026")
    pdf.new_page()

    pdf.line("Цель работы", bold=True)
    pdf.line(spec["goal"])
    pdf.line("Основные этапы работы", bold=True)
    for index, stage in enumerate(spec["stages"], start=1):
        pdf.line(f"{index}. {stage}")
    pdf.line("Ход выполнения и результаты", bold=True)
    for caption, headers, rows in spec["tables"]:
        pdf.line(caption, bold=True)
        pdf.line(" | ".join(headers))
        for row in rows:
            pdf.line(" | ".join(str(x) for x in row))
        pdf.line()
    for image_name, caption in spec["images"]:
        pdf.image(folder / image_name, caption)
    pdf.line("Вывод", bold=True)
    pdf.line(spec["conclusion"])
    pdf.new_page()
    pdf.line("Фрагменты кода из main.ipynb", bold=True)
    for chunk in notebook_code(folder / "main.ipynb")[:10]:
        for line in chunk.splitlines()[:45]:
            pdf.line(line[:120], mono=True)
        pdf.line()
    pdf.save()
    return out


def main() -> None:
    docx = build_docx(LAB_NUMBER, SPEC)
    pdf = build_pdf(LAB_NUMBER, SPEC)
    print(f"created {docx.name}")
    print(f"created {pdf.name}")


if __name__ == "__main__":
    main()
