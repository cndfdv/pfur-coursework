import pytest

from app.core.exceptions import ValidationError
from app.core.models import Transaction
from app.services.validator import validate


def test_valid_record_returns_transaction(good_record):
    tx = validate(good_record)
    assert isinstance(tx, Transaction)
    assert tx.amount == 100.5
    assert tx.category == "food"


@pytest.mark.parametrize(
    "amount, valid",
    [
        ("0.01", True),
        ("100", True),
        ("1e6", True),
        ("0", False),
        ("-1", False),
        ("-0.01", False),
        ("abc", False),
        ("", False),
        (None, False),
    ],
)
def test_amount_boundaries(good_record, amount, valid):
    good_record["amount"] = amount
    if valid:
        validate(good_record)
    else:
        with pytest.raises(ValidationError):
            validate(good_record)


@pytest.mark.parametrize("missing_field", ["id", "amount", "category", "date"])
def test_missing_field_raises(good_record, missing_field):
    del good_record[missing_field]
    with pytest.raises(ValidationError):
        validate(good_record)


@pytest.mark.parametrize("empty_field", ["id", "amount", "category", "date"])
def test_empty_field_raises(good_record, empty_field):
    good_record[empty_field] = ""
    with pytest.raises(ValidationError):
        validate(good_record)


def test_garbage_input_does_not_crash():
    """На любой мусор должен прилетать ValidationError, а не что-то другое."""
    with pytest.raises(ValidationError):
        validate({"junk": "data"})
