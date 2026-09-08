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


def test_citation_version_matches():
    """RELEASE.md step 3 promises three files in lockstep; two were guarded.

    CITATION.cff is the citable record of the release (§ Authorship / FAIR
    posture), so a version it disagrees with is a wrong DOI-level claim, not a
    typo. Parsed by regex rather than YAML: the file is not otherwise read at
    runtime and this test must not add a dependency to do it.
    """
    import re
    from pathlib import Path
    import iladub

    cff = (Path(__file__).resolve().parent.parent / "CITATION.cff").read_text()
    m = re.search(r'(?m)^version:\s*"?([^"\s]+)"?\s*$', cff)
    assert m, "CITATION.cff has no top-level version: field"
    assert m.group(1) == iladub.__version__
