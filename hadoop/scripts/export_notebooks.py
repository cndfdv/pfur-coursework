"""Экспорт выполненных ноутбуков в PDF через установленный Chrome."""

import argparse
import re
import subprocess
import tempfile
from pathlib import Path

import nbformat
from nbconvert import HTMLExporter

PRINT_CSS = """
<style>
@page { size: A4; margin: 14mm 12mm; }
@media print {
  html, body { margin: 0 !important; padding: 0 !important; }
  #notebook { padding: 0 !important; }
  #notebook-container {
    width: auto !important; padding: 0 !important;
    box-shadow: none !important;
  }
  .container { width: auto !important; }
  .cell { padding: 4px 0 !important; break-inside: auto; }
  .prompt { display: none !important; }
  .inner_cell, .output_area, .output_subarea {
    width: 100% !important; max-width: 100% !important;
    min-width: 0 !important;
  }
  .text_cell_render { padding: 3px 0 !important; font-size: 11px; }
  .text_cell_render h2 { font-size: 17px; }
  .text_cell_render h3 { font-size: 14px; }
  .text_cell_render h4 { font-size: 12px; }
  h1, h2, h3, h4 { break-after: avoid; }
  pre, code, .highlight pre {
    font-family: Menlo, monospace !important;
    font-size: 10px !important; line-height: 1.35 !important;
    white-space: pre-wrap !important; overflow-wrap: anywhere !important;
    word-break: break-all !important;
  }
  .output_subarea pre { font-size: 9px !important; }
  p code {
    white-space: nowrap !important; overflow-wrap: normal !important;
    word-break: normal !important;
  }
  .output_stderr { display: none !important; }
  .output_png, .output_html table { break-inside: avoid; }
  .output_png img { max-width: 100% !important; max-height: 235mm; object-fit: contain; }
  table { font-size: 9px !important; }
  .output_scroll { height: auto !important; box-shadow: none !important; }
}
</style>
"""


def split_wide_tables(text: str, width: int = 120) -> str:
    """Делим широкие таблицы Spark по столбцам, сохраняя все значения."""
    lines = text.splitlines()
    result = []
    index = 0
    border_pattern = re.compile(r"\+(?:-+\+)+$")
    while index < len(lines):
        border = lines[index]
        if (
            len(border) <= width
            or not border_pattern.fullmatch(border)
            or index + 2 >= len(lines)
            or lines[index + 2] != border
            or not lines[index + 1].startswith("|")
        ):
            result.append(lines[index])
            index += 1
            continue
        end = index + 3
        while end < len(lines) and lines[end].startswith("|"):
            end += 1
        if end >= len(lines) or lines[end] != border:
            result.append(lines[index])
            index += 1
            continue

        lengths = [len(part) for part in border.split("+")[1:-1]]
        rows = [lines[index + 1].split("|")[1:-1]]
        rows.extend(line.split("|")[1:-1] for line in lines[index + 3 : end])
        if any(len(row) != len(lengths) for row in rows):
            result.append(lines[index])
            index += 1
            continue

        groups = []
        columns = [0]
        used = lengths[0] + 2
        for column in range(1, len(lengths)):
            if used + lengths[column] + 1 > width and len(columns) > 1:
                groups.append(columns)
                columns = [0]
                used = lengths[0] + 2
            columns.append(column)
            used += lengths[column] + 1
        groups.append(columns)

        for group in groups:
            if result and result[-1] != "":
                result.append("")
            separator = "+" + "+".join("-" * lengths[c] for c in group) + "+"
            result.extend([separator, "|" + "|".join(rows[0][c] for c in group) + "|", separator])
            result.extend("|" + "|".join(row[c] for c in group) + "|" for row in rows[1:])
            result.append(separator)
        index = end + 1
    return "\n".join(result) + ("\n" if text.endswith("\n") else "")


def export_notebook(path: Path, chrome: Path) -> Path:
    notebook = nbformat.read(path, as_version=4)
    nbformat.validate(notebook)
    for index, cell in enumerate(notebook.cells):
        if cell.cell_type != "code" or not cell.source.strip():
            continue
        if cell.execution_count is None:
            raise ValueError(f"{path}: ячейка {index} не выполнена")
        if any(output.output_type == "error" for output in cell.outputs):
            raise ValueError(f"{path}: ошибка в ячейке {index}")
        for output in cell.outputs:
            if output.output_type == "stream":
                output.text = split_wide_tables(output.text)

    exporter = HTMLExporter(template_name="classic")
    exporter.exclude_input_prompt = True
    exporter.exclude_output_prompt = True
    body, _ = exporter.from_notebook_node(notebook)
    body = body.replace("</head>", PRINT_CSS + "</head>")
    destination = path.with_suffix(".pdf")

    with tempfile.TemporaryDirectory(prefix="notebook-pdf-") as directory:
        temporary = Path(directory)
        html_path = temporary / "notebook.html"
        html_path.write_text(body, encoding="utf-8")
        pdf_path = temporary / "notebook.pdf"
        subprocess.run(
            [
                str(chrome),
                "--headless",
                "--disable-gpu",
                "--no-pdf-header-footer",
                "--disable-background-networking",
                f"--user-data-dir={temporary / 'chrome'}",
                f"--print-to-pdf={pdf_path}",
                html_path.as_uri(),
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if not pdf_path.is_file() or pdf_path.stat().st_size < 1000:
            raise RuntimeError(f"PDF для {path} не создан")
        destination.write_bytes(pdf_path.read_bytes())
    return destination


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("notebooks", nargs="*", type=Path)
    parser.add_argument(
        "--chrome",
        type=Path,
        default=Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    )
    arguments = parser.parse_args()
    if not arguments.chrome.is_file():
        parser.error("Chrome не найден: укажите путь через --chrome")
    paths = arguments.notebooks or [root / f"lab_{i}/main.ipynb" for i in (3, 4, 5)]
    for path in paths:
        print(export_notebook(path.resolve(), arguments.chrome), flush=True)


if __name__ == "__main__":
    main()
