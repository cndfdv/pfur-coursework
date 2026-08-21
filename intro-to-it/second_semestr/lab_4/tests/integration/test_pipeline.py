import json
from pathlib import Path

from main import process_file, run


def test_csv_with_mixed_rows(mixed_csv):
    """1 хорошая + 2 битых строки → 1 транзакция, 2 ошибки."""
    transactions, errors = process_file(mixed_csv)
    assert len(transactions) == 1
    assert len(errors) == 2
    assert transactions[0].amount == 100.0


def test_run_aggregates_categories(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    csv = data_dir / "x.csv"
    csv.write_text(
        "id,amount,category,date\n"
        "1,100,food,2025-09-01\n"
        "2,50,food,2025-09-02\n"
        "3,200,rent,2025-09-03\n",
        encoding="utf-8",
    )
    output = tmp_path / "result.json"

    totals = run(data_dir, output)

    assert totals == {"food": 150.0, "rent": 200.0}
    assert json.loads(output.read_text()) == {"food": 150.0, "rent": 200.0}


def test_run_skips_unknown_extensions(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "ignore.txt").write_text("whatever")
    csv = data_dir / "ok.csv"
    csv.write_text(
        "id,amount,category,date\n1,10,food,2025-09-01\n",
        encoding="utf-8",
    )
    output = tmp_path / "result.json"

    totals = run(data_dir, output)
    assert totals == {"food": 10.0}


def test_broken_json_is_handled(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "broken.json").write_text("{not valid")
    output = tmp_path / "result.json"

    totals = run(data_dir, output)
    assert totals == {}


def test_csv_missing_columns_is_handled(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "weird.csv").write_text("foo,bar\n1,2\n", encoding="utf-8")
    output = tmp_path / "result.json"
    totals = run(data_dir, output)
    assert totals == {}
