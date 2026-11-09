# Лабораторные работы

Для всех работ используется окружение `hadoop`.

```bash
mamba env create -f environment.yml
mamba activate hadoop
jupyter lab
```

В Jupyter нужно выбрать ядро `Python (hadoop)`.

В лабораторной 3 рядом с ноутбуком лежит
`WA_Fn-UseC_-Telco-Customer-Churn.csv`, в работах 4 и 5 — `adult.data`.
Telco взят из [репозитория IBM](https://github.com/IBM/telco-customer-churn-on-icp4d/tree/master/data),
Adult — из [UCI](https://archive.ics.uci.edu/dataset/2/adult).

Повторный запуск работы из её каталога:

```bash
mamba run -n hadoop jupyter nbconvert --to notebook --execute --inplace main.ipynb --ExecutePreprocessor.timeout=600
```

По умолчанию скрипт экспортирует ноутбуки лабораторных 3–5 в PDF рядом с ними. Для экспорта нужен установленный Google Chrome:

```bash
mamba run -n hadoop python scripts/export_notebooks.py
```

Экспорт использует сохранённые результаты: все кодовые ячейки должны быть выполнены
и не содержать ошибок. Отдельные ноутбуки можно передать позиционными аргументами;
путь к Chrome в другом каталоге задаётся через `--chrome`.
Широкие таблицы в PDF разделяются по столбцам с повторением первого столбца;
все значения сохраняются. Служебные предупреждения Spark остаются в ноутбуке.
