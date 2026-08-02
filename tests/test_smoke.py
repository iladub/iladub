import iladub


def test_version_is_exposed():
    assert isinstance(iladub.__version__, str)
    assert iladub.__version__


def test_version_single_source():
    import tomllib
    from pathlib import Path
    import iladub
    pyproject = tomllib.load(open(Path(__file__).resolve().parent.parent / "pyproject.toml", "rb"))
    assert iladub.__version__ == pyproject["project"]["version"]
