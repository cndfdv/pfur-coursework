"""Выполняет main.ipynb выбранной лабы, сохраняя все графики в figures/lab{N}_NN.png.

Запуск: python run_lab.py <N>
Графики (plt.show) перехватываются и сохраняются по порядку; stdout пишется в log.
"""
import io as _io
import json
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
N = int(sys.argv[1])
lab = ROOT / f"lab_{N}"
fig_dir = lab / "figures"
fig_dir.mkdir(exist_ok=True)

counter = {"i": 0}
_orig_show = plt.show


def _save_show(*args, **kwargs):
    for num in plt.get_fignums():
        counter["i"] += 1
        fig = plt.figure(num)
        fig.savefig(fig_dir / f"lab{N}_fig{counter['i']:02d}.png", dpi=130, bbox_inches="tight")
    plt.close("all")


plt.show = _save_show

nb = json.loads((lab / "main.ipynb").read_text(encoding="utf-8"))
code_cells = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]

os.chdir(lab)
ns: dict = {"__name__": "__main__"}
log = _io.StringIO()
with redirect_stdout(log):
    for idx, src in enumerate(code_cells):
        try:
            exec(compile(src, f"cell_{idx}", "exec"), ns)
        except Exception as exc:  # noqa
            print(f"\n!!! ОШИБКА в ячейке {idx}: {type(exc).__name__}: {exc}")
            import traceback
            traceback.print_exc(file=sys.stdout)
            break

text = log.getvalue()
(fig_dir / f"lab{N}_log.txt").write_text(text, encoding="utf-8")
print(text[-2500:])
print(f"\n[saved {counter['i']} figures to {fig_dir}]")
