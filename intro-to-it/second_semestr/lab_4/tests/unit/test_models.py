from app.core.models import Transaction


def test_transaction_fields():
    t = Transaction(id="x", amount=10.5, category="food", date="2025-09-01")
    assert t.id == "x"
    assert t.amount == 10.5


def test_transaction_equality():
    a = Transaction(id="1", amount=1.0, category="c", date="d")
    b = Transaction(id="1", amount=1.0, category="c", date="d")
    assert a == b
