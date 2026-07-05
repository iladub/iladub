def test_public_api_exports():
    import iladub.etkl as e
    for name in ["compile_tables", "CompilationReport", "RegionReport",
                 "RegionKind", "Cell"]:
        assert hasattr(e, name), f"missing export: {name}"
