import pytest


@pytest.fixture
def good_record() -> dict:
    return {
        "id": "tx-1",
        "amount": "100.50",
        "category": "food",
        "date": "2025-09-01",
    }


@pytest.fixture
def good_csv(tmp_path):
    """Создаёт CSV с одной валидной строкой."""
    p = tmp_path / "good.csv"
    p.write_text(
        "id,amount,category,date\n"
        "1,100.0,food,2025-09-01\n",
        encoding="utf-8",
    )
    return p


@pytest.fixture
def mixed_csv(tmp_path):
    """CSV с одной хорошей строкой и двумя битыми."""
    p = tmp_path / "mixed.csv"
    p.write_text(
        "id,amount,category,date\n"
        "1,100.0,food,2025-09-01\n"
        "2,abc,food,2025-09-02\n"
        "3,-50,food,2025-09-03\n",
        encoding="utf-8",
    )
    return p
