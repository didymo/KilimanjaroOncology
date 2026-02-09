import pytest


def test_main_success_exits_zero(monkeypatch):
    import kilimanjaro_oncology.main as main_mod

    class _App:
        def run(self):
            return None

    monkeypatch.setattr(main_mod, "MainApp", _App)
    with pytest.raises(SystemExit) as excinfo:
        main_mod.main()
    assert excinfo.value.code == 0


def test_main_exception_exits_one_and_logs(monkeypatch):
    import kilimanjaro_oncology.main as main_mod

    class _App:
        def run(self):
            raise RuntimeError("boom")

    calls = {}

    def fake_exception(message):
        calls["message"] = message

    monkeypatch.setattr(main_mod, "MainApp", _App)
    monkeypatch.setattr(main_mod.logger, "exception", fake_exception)
    with pytest.raises(SystemExit) as excinfo:
        main_mod.main()
    assert excinfo.value.code == 1
    assert "Critical error" in calls["message"]
