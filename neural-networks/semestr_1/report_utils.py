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
import re
import shutil
import subprocess
import textwrap
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
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


def figure(caption: str, image: str | None = None, width_cm: float = 15) -> tuple:
    return ("fig", caption, image, width_cm)


def _number_caption(caption: str, n: int) -> str:
    """Возвращает подпись вида «Рис. N — …», убирая прежнюю нумерацию, если была.

    Гарантирует сквозную нумерацию всех рисунков (включая схемы) в отчёте.
    """
    stripped = re.sub(r"^Рис\.\s*\d+\s*[—-]\s*", "", caption).strip()
    return f"Рис. {n} — {stripped}"


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
# Основной шрифт отчёта — Times New Roman (по требованию к оформлению).
DOC_FONT = "Times New Roman"

# Готовый титульный лист (на основе образца преподавателя titl_list.docx,
# с доведённым до нужного вида блоком подписей). Отчёт собирается поверх него,
# чтобы титул и нижний колонтитул («Москва, 2026») в точности совпадали с эталоном.
# Номер и название работы, а также номер варианта подставляются вместо «##».
TEMPLATE = Path(__file__).resolve().parent / "titl_template.docx"


def _set_font(run, name: str = DOC_FONT) -> None:
    run.font.name = name
    # Для корректного отображения кириллицы задаём шрифт и для восточноевропейской
    # таблицы символов (атрибут w:eastAsia/cs в rPr).
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        rfonts.set(qn(attr), name)


def _doc_setup() -> Document:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Emu(914400)
    section.bottom_margin = Emu(914400)
    section.left_margin = Emu(1143000)
    section.right_margin = Emu(1143000)
    style = doc.styles["Normal"]
    style.font.name = DOC_FONT
    style.font.size = Pt(14)
    style.paragraph_format.space_after = Pt(0)
    style.paragraph_format.space_before = Pt(0)
    style.paragraph_format.line_spacing = 1.15
    return doc


def _body_fmt(p) -> None:
    """Оформление абзаца тела отчёта: интервал 1.15, без отбивок."""
    pf = p.paragraph_format
    pf.line_spacing = 1.15
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)


def _centered(doc: Document, text: str, bold_text: bool = False) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    _set_font(run)
    run.font.size = Pt(14)
    run.bold = bold_text


def _normal(doc: Document, text: str, bold_text: bool = False, justify: bool = False) -> None:
    p = doc.add_paragraph()
    _body_fmt(p)
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    run = p.add_run(text)
    _set_font(run)
    run.font.size = Pt(14)
    run.bold = bold_text


def _mixed(doc: Document, parts: list[tuple[str, bool]], justify: bool = False) -> None:
    p = doc.add_paragraph()
    _body_fmt(p)
    if justify:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for text, bold_text in parts:
        run = p.add_run(text)
        _set_font(run)
        run.font.size = Pt(14)
        run.bold = bold_text


def _code(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    _body_fmt(p)
    run = p.add_run(text)
    run.font.size = Pt(10)
    run.font.name = "Courier New"


def _empty(doc: Document, n: int = 1) -> None:
    for _ in range(n):
        doc.add_paragraph()


def _figure_docx(doc: Document, caption: str, image: str | None, folder: Path,
                 width_cm: float = 15) -> None:
    p = doc.add_paragraph()
    _body_fmt(p)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    # Не даём оторвать рисунок от его подписи при переносе на новую страницу.
    p.paragraph_format.keep_with_next = True
    image_path = (folder / image) if image else None
    if image_path and image_path.exists():
        p.add_run().add_picture(str(image_path), width=Cm(width_cm))
    else:
        run = p.add_run("[ВСТАВИТЬ РИСУНОК]")
        run.font.size = Pt(12)
        run.italic = True
    cap = doc.add_paragraph()
    _body_fmt(cap)
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap_run = cap.add_run(caption)
    _set_font(cap_run)
    cap_run.font.size = Pt(12)


def _table_borders(t) -> None:
    """Добавляет сплошную сетку таблице через XML (без зависимости от стиля)."""
    tbl_pr = t._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), "000000")
        borders.append(el)
    tbl_pr.append(borders)


def _table(doc: Document, headers: list[str], rows: list[list]) -> None:
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    _table_borders(t)
    def _fill(cell, value, bold_text=False):
        cell.text = str(value)
        for p in cell.paragraphs:
            _body_fmt(p)
            for run in p.runs:
                _set_font(run)
                run.font.size = Pt(12)
                run.bold = bold_text

    for i, header in enumerate(headers):
        _fill(t.rows[0].cells[i], header, bold_text=True)
    for r, row in enumerate(rows, start=1):
        for c, value in enumerate(row):
            _fill(t.rows[r].cells[c], value)


def _right(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run(text)
    _set_font(run)
    run.font.size = Pt(14)


def _clear_footer(footer) -> None:
    """Оставляет в колонтитуле один пустой абзац (без прежнего содержимого)."""
    paras = footer.paragraphs
    for p in paras[1:]:
        p._element.getparent().remove(p._element)
    for r in list(paras[0].runs):
        r._element.getparent().remove(r._element)


def _add_page_number(run) -> None:
    """Вставляет в run поле автонумерации страницы (PAGE)."""
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.append(begin)
    run._r.append(instr)
    run._r.append(end)


def _setup_footers(doc: Document) -> None:
    """Титул — «Москва, 2026»; остальные страницы — номер страницы по центру."""
    sec = doc.sections[0]
    sec.different_first_page_header_footer = True

    first = sec.first_page_footer
    first.is_linked_to_previous = False
    _clear_footer(first)
    fp = first.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = fp.add_run("Москва, 2026")
    _set_font(run)
    run.font.size = Pt(14)

    rest = sec.footer
    rest.is_linked_to_previous = False
    _clear_footer(rest)
    pn = rest.paragraphs[0]
    pn.alignment = WD_ALIGN_PARAGRAPH.CENTER
    num_run = pn.add_run()
    _set_font(num_run)
    num_run.font.size = Pt(12)
    _add_page_number(num_run)


def _open_with_title(number: int, title: str, variant: str) -> Document:
    """Открывает образец титульного листа и подставляет данные работы.

    Титул и нижний колонтитул («Москва, 2026») берутся прямо из titl_template.docx,
    поэтому полностью совпадают с эталоном (включая выверенный блок подписей).
    Заполняются только номер и название работы и номер варианта — остальное
    оформление (шрифты, отступы, интервалы, колонтитул) сохраняется без изменений.
    """
    doc = Document(str(TEMPLATE))
    for p in doc.paragraphs:
        txt = p.text
        if txt.startswith("о выполнении лабораторной работы"):
            # runs: [..№ ', '##', ' “##”'] — заменяем номер и название работы.
            runs = p.runs
            for i, r in enumerate(runs):
                if r.text == "##":
                    r.text = str(number)
                    if i + 1 < len(runs):
                        runs[i + 1].text = f" “{title}”"
                        for extra in runs[i + 2:]:
                            extra.text = ""
                    break
        elif txt.startswith("Вариант задания"):
            for r in p.runs:
                if r.text == "##":
                    r.text = str(variant)
    doc.add_page_break()
    return doc


def _render_blocks_docx(doc: Document, blocks: list[tuple], folder: Path) -> None:
    fig_no = 0
    for block in blocks:
        kind = block[0]
        if kind == "h":
            _normal(doc, block[1], bold_text=True)
            _empty(doc)
        elif kind == "p":
            _normal(doc, block[1], justify=True)
            _empty(doc)
        elif kind == "b":
            _normal(doc, block[1], bold_text=True)
        elif kind == "table":
            _normal(doc, block[1])
            _table(doc, block[2], block[3])
            _empty(doc)
        elif kind == "fig":
            fig_no += 1
            width_cm = block[3] if len(block) > 3 else 15
            _figure_docx(doc, _number_caption(block[1], fig_no), block[2], folder, width_cm)
            _empty(doc)
        elif kind == "pb":
            doc.add_page_break()


def _build_docx(out: Path, number: int, title: str, variant: str, goal: str,
                stages: list[str], equipment: str, blocks: list[tuple],
                conclusion: list[str], notebook: Path) -> None:
    doc = _open_with_title(number, title, variant)
    _setup_footers(doc)

    _mixed(doc, [("Цель работы: ", True), (goal, False)], justify=True)
    _empty(doc)
    _normal(doc, "Основные этапы работы:", bold_text=True)
    for i, stage in enumerate(stages, start=1):
        _normal(doc, f"{i}. {stage}", justify=True)
    _empty(doc)
    _mixed(doc, [("Программное обеспечение: ", True), (equipment, False)], justify=True)
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
        _normal(doc, paragraph, justify=True)
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
    pdf.y += 40
    for part in ("ФЕДЕРАЛЬНОЕ ГОСУДАРСТВЕННОЕ АВТОНОМНОЕ ОБРАЗОВАТЕЛЬНОЕ",
                 "УЧРЕЖДЕНИЕ ВЫСШЕГО ОБРАЗОВАНИЯ",
                 "РОССИЙСКИЙ УНИВЕРСИТЕТ ДРУЖБЫ НАРОДОВ", "ИМЕНИ ПАТРИСА ЛУМУМБЫ"):
        pdf.center(part, font=pdf.small)
    pdf.y += 16
    pdf.center("Факультет искусственного интеллекта", font=pdf.small)
    pdf.y += 110
    pdf.center("Отчет")
    title_line = f'о выполнении лабораторной работы № {number} "{title}"'
    for part in textwrap.wrap(title_line, width=46):
        pdf.center(part)
    pdf.center('по дисциплине "Нейронные сети"')
    pdf.center(f"Вариант задания № {variant}")
    pdf.y += 120
    pdf.line("Выполнил студент группы ЗФИбд-01-24: Князев А. М.")
    pdf.line("Проверил и принял: доцент кафедры прикладного ИИ Леонов С.С.")
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

    fig_no = 0
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
            fig_no += 1
            image_path = (notebook.parent / block[2]) if block[2] else None
            pdf.image(image_path if image_path else Path("/nonexistent"),
                      _number_caption(block[1], fig_no))
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
def _find_soffice() -> str | None:
    """Ищет исполняемый файл LibreOffice (soffice) в PATH и стандартных местах."""
    for name in ("soffice", "libreoffice"):
        path = shutil.which(name)
        if path:
            return path
    mac_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    return mac_path if Path(mac_path).exists() else None


def _convert_with_soffice(docx_path: Path, folder: Path) -> bool:
    """Конвертирует docx → pdf через LibreOffice. Возвращает True при успехе."""
    soffice = _find_soffice()
    if not soffice:
        return False
    try:
        subprocess.run(
            [soffice, "--headless", "--convert-to", "pdf", "--outdir",
             str(folder), str(docx_path)],
            check=True, capture_output=True, timeout=180,
        )
    except (subprocess.SubprocessError, OSError):
        return False
    return (folder / f"{docx_path.stem}.pdf").exists()


def build_report(*, number: int, title: str, variant: str, goal: str,
                 stages: list[str], equipment: str, blocks: list[tuple],
                 conclusion: list[str], folder: Path) -> None:
    notebook = folder / "main.ipynb"
    docx_path = folder / f"report_lab{number}.docx"
    pdf_path = folder / f"report_lab{number}.pdf"
    _build_docx(docx_path, number, title, variant, goal, stages, equipment,
                blocks, conclusion, notebook)
    print(f"created {docx_path.name}")
    # Если доступен LibreOffice — конвертируем docx в «вордовский» PDF (точное
    # отображение шрифтов, выравнивания, таблиц). Иначе строим растровый PDF.
    if _convert_with_soffice(docx_path, folder):
        print(f"created {pdf_path.name} (LibreOffice)")
    else:
        _build_pdf(pdf_path, number, title, variant, goal, stages, equipment,
                   blocks, conclusion, notebook)
        print(f"created {pdf_path.name} (raster fallback)")
