class _DummyDB:
    def __init__(self, _path):
        pass


class _DummyFocus:
    def __init__(self):
        self.focused = False

    def focus_set(self):
        self.focused = True


class _DummyScreen:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def pack(self, *args, **kwargs):
        return None

    def destroy(self):
        return None


class _DummyNewDx(_DummyScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patient_id_entry = _DummyFocus()


class _DummyFollowUp(_DummyScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patient_id_combo = _DummyFocus()


class _DummyDeath(_DummyScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patient_id_combo = _DummyFocus()


def _make_config_manager(exists, init_calls):
    class _DummyConfigManager:
        def __init__(self):
            self.settings = {"db_path": "fake.sqlite"}

        def config_exists(self):
            return exists

        def initialize_database(self):
            init_calls.append("init")

    return _DummyConfigManager


def test_main_app_shows_config_screen_when_missing(monkeypatch):
    import kilimanjaro_oncology.gui.main_app as main_app

    init_calls = []
    monkeypatch.setattr(
        main_app,
        "ConfigManager",
        _make_config_manager(False, init_calls),
    )
    monkeypatch.setattr(main_app, "DatabaseService", _DummyDB)
    monkeypatch.setattr(main_app, "ConfigScreen", _DummyScreen)
    monkeypatch.setattr(main_app, "NewDiagnosisScreen", _DummyNewDx)
    monkeypatch.setattr(main_app, "FollowUpScreen", _DummyFollowUp)
    monkeypatch.setattr(main_app, "DeathScreen", _DummyDeath)

    app = main_app.MainApp()
    app.withdraw()
    try:
        assert isinstance(app.current_screen, _DummyScreen)
        assert init_calls == []
    finally:
        app.destroy()


def test_main_app_shows_new_diagnosis_when_ready(monkeypatch):
    import kilimanjaro_oncology.gui.main_app as main_app

    init_calls = []
    monkeypatch.setattr(
        main_app,
        "ConfigManager",
        _make_config_manager(True, init_calls),
    )
    monkeypatch.setattr(main_app, "DatabaseService", _DummyDB)
    monkeypatch.setattr(main_app, "ConfigScreen", _DummyScreen)
    monkeypatch.setattr(main_app, "NewDiagnosisScreen", _DummyNewDx)
    monkeypatch.setattr(main_app, "FollowUpScreen", _DummyFollowUp)
    monkeypatch.setattr(main_app, "DeathScreen", _DummyDeath)

    app = main_app.MainApp()
    app.withdraw()
    try:
        assert isinstance(app.current_screen, _DummyNewDx)
        assert init_calls == ["init"]
        assert app.current_screen.patient_id_entry.focused is True
    finally:
        app.destroy()


def test_main_app_show_followup_and_death_focus(monkeypatch):
    import kilimanjaro_oncology.gui.main_app as main_app

    init_calls = []
    monkeypatch.setattr(
        main_app,
        "ConfigManager",
        _make_config_manager(False, init_calls),
    )
    monkeypatch.setattr(main_app, "DatabaseService", _DummyDB)
    monkeypatch.setattr(main_app, "ConfigScreen", _DummyScreen)
    monkeypatch.setattr(main_app, "NewDiagnosisScreen", _DummyNewDx)
    monkeypatch.setattr(main_app, "FollowUpScreen", _DummyFollowUp)
    monkeypatch.setattr(main_app, "DeathScreen", _DummyDeath)

    app = main_app.MainApp()
    app.withdraw()
    try:
        app.show_followup_screen()
        assert isinstance(app.current_screen, _DummyFollowUp)
        assert app.current_screen.patient_id_combo.focused is True

        app.show_death_screen()
        assert isinstance(app.current_screen, _DummyDeath)
        assert app.current_screen.patient_id_combo.focused is True
    finally:
        app.destroy()
