import tkinter as tk

import pytest


@pytest.fixture
def tk_root():
    root = tk.Tk()
    root.withdraw()
    yield root
    root.destroy()


class _DummyConfigManager:
    def __init__(self, db_path):
        self.settings = {"db_path": db_path, "font_size": 14}


def test_application_shows_config_when_db_missing(monkeypatch):
    import kilimanjaro_oncology.gui.app as app_mod

    def fake_config():
        return _DummyConfigManager("")

    called = {"config": False, "main": False}

    monkeypatch.setattr(app_mod, "ConfigManager", fake_config)
    monkeypatch.setattr(
        app_mod.Application,
        "show_config_screen",
        lambda self: called.__setitem__("config", True),
    )
    monkeypatch.setattr(
        app_mod.Application,
        "show_main_screen",
        lambda self: called.__setitem__("main", True),
    )

    app = app_mod.Application()
    app.withdraw()
    try:
        assert called["config"] is True
        assert called["main"] is False
    finally:
        app.destroy()


def test_application_shows_main_when_db_present(monkeypatch):
    import kilimanjaro_oncology.gui.app as app_mod

    def fake_config():
        return _DummyConfigManager("/tmp/db.sqlite")

    called = {"config": False, "main": False}

    monkeypatch.setattr(app_mod, "ConfigManager", fake_config)
    monkeypatch.setattr(
        app_mod.Application,
        "show_config_screen",
        lambda self: called.__setitem__("config", True),
    )
    monkeypatch.setattr(
        app_mod.Application,
        "show_main_screen",
        lambda self: called.__setitem__("main", True),
    )

    app = app_mod.Application()
    app.withdraw()
    try:
        assert called["main"] is True
        assert called["config"] is False
    finally:
        app.destroy()


def test_apply_font_size_updates_named_font(monkeypatch):
    import tkinter.font as tkfont
    import kilimanjaro_oncology.gui.app as app_mod

    def fake_config():
        return _DummyConfigManager("/tmp/db.sqlite")

    monkeypatch.setattr(app_mod, "ConfigManager", fake_config)
    monkeypatch.setattr(
        app_mod.Application,
        "show_main_screen",
        lambda _self: None,
    )

    app = app_mod.Application()
    app.withdraw()
    try:
        app.apply_font_size()
        default = tkfont.nametofont("TkDefaultFont")
        assert int(default.cget("size")) == 14
    finally:
        app.destroy()
