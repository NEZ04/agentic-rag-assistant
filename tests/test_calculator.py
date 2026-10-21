import pytest

from app.calculator import safe_eval


def test_basic_arithmetic():
    assert safe_eval("17 * 23") == 391
    assert safe_eval("(2 + 3) ** 2") == 25
    assert safe_eval("10 / 4") == 2.5
    assert safe_eval("-3 + 5") == 2


def test_caret_means_power():
    assert safe_eval("2^10") == 1024


@pytest.mark.parametrize("bad", [
    "__import__('os').system('dir')",
    "open('x.txt')",
    "a + 1",
    "[1, 2, 3]",
    "2 ** 100000",
])
def test_rejects_anything_but_arithmetic(bad):
    with pytest.raises(ValueError):
        safe_eval(bad)
