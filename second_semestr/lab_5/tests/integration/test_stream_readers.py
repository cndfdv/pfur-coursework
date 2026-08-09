from app.io.transactions import read_transactions


def test_read_transactions_dispatches_csv(good_csv):
    rows = read_transactions(good_csv)
    assert iter(rows) is rows
    assert next(rows)["id"] == "1"


def test_json_reader_streams_array(tmp_path):
    path = tmp_path / "transactions.json"
    path.write_text(
        '[{"id": "1", "amount": "10", "category": "food", "date": "2025-09-01"},'
        '{"id": "2", "amount": "20", "category": "rent", "date": "2025-09-02"}]',
        encoding="utf-8",
    )

    rows = read_transactions(path)
    assert iter(rows) is rows
    assert next(rows)["category"] == "food"
    assert next(rows)["category"] == "rent"
