import pytest


def _make_app(main_app, raise_exc):
    app = main_app.MainApp.__new__(main_app.MainApp)
    app.mainloop = lambda: (_ for _ in ()).throw(raise_exc)
    app.show_config_screen = lambda: setattr(app, "_shown", True)
    return app


def test_run_handles_configuration_error(monkeypatch):
    import kilimanjaro_oncology.gui.main_app as main_app

    app = _make_app(main_app, main_app.ConfigurationError())
    called = {}

    monkeypatch.setattr(main_app.logger, "error", lambda msg: called.setdefault("e", msg))
    app.run()
    assert getattr(app, "_shown", False) is True
    assert "Configuration failed" in called["e"]


def test_run_handles_database_error(monkeypatch):
    import kilimanjaro_oncology.gui.main_app as main_app

    app = _make_app(main_app, main_app.DatabaseError())
    monkeypatch.setattr(main_app.logger, "error", lambda _msg: None)

    with pytest.raises(SystemExit) as excinfo:
        app.run()
    assert excinfo.value.code == 3


def test_run_handles_unexpected_error(monkeypatch):
    import kilimanjaro_oncology.gui.main_app as main_app

    app = _make_app(main_app, RuntimeError("boom"))
    monkeypatch.setattr(main_app.logger, "exception", lambda _msg: None)

    with pytest.raises(SystemExit) as excinfo:
        app.run()
    assert excinfo.value.code == 1
