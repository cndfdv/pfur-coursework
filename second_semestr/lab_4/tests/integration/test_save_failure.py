from unittest.mock import patch

import pytest

from main import save_result


def test_save_result_propagates_disk_error(tmp_path):
    """Если запись на диск падает, ошибка должна быть видна."""
    output = tmp_path / "result.json"

    with patch("main.os.replace", side_effect=OSError("read-only filesystem")):
        with pytest.raises(OSError, match="read-only"):
            save_result({"food": 100.0}, output)


def test_save_result_atomic_write(tmp_path):
    """Должен использоваться временный файл + rename."""
    output = tmp_path / "result.json"
    seen = {}

    real_replace = __import__("os").replace

    def spy(src, dst):
        seen["src"] = str(src)
        seen["dst"] = str(dst)
        real_replace(src, dst)

    with patch("main.os.replace", side_effect=spy):
        save_result({"food": 100.0}, output)

    assert seen["src"].endswith(".tmp")
    assert seen["dst"] == str(output)
    assert output.exists()
