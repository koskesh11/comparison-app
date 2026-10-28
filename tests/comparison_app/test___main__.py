"""python -m comparison_app (src/comparison_app/__main__.py) starts app/main.main."""

import runpy

import comparison_app.app.main as app_main


def test_the_module_starts_main(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    started = []
    monkeypatch.setattr(app_main, "main", lambda: started.append(True))
    runpy.run_module("comparison_app", run_name="__main__")
    assert started == [True]
