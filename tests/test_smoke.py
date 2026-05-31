import iladub


def test_version_is_exposed():
    assert isinstance(iladub.__version__, str)
    assert iladub.__version__
