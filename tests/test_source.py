import pytest

from vim_python.source import PyModule


def test_analyze():
    assert isinstance(PyModule.by_source(''), PyModule)
    with pytest.raises(SyntaxError):
        PyModule.by_source(',')


