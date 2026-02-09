import logging


def test_setup_logger_adds_handlers(monkeypatch, tmp_path):
    import kilimanjaro_oncology.utils.logger as logger_mod

    logger_mod.logging.getLogger("AfricaOncologyApp").handlers.clear()
    monkeypatch.setattr(
        logger_mod, "LOG_FILE", tmp_path / "app.log", raising=True
    )

    logger = logger_mod.setup_logger()
    assert logger.name == "AfricaOncologyApp"
    assert logger.level == logging.DEBUG

    file_handlers = [
        h for h in logger.handlers if isinstance(h, logging.FileHandler)
    ]
    stream_handlers = [
        h
        for h in logger.handlers
        if isinstance(h, logging.StreamHandler)
        and not isinstance(h, logging.FileHandler)
    ]
    assert file_handlers
    assert stream_handlers
    assert file_handlers[0].level == logging.INFO
    assert stream_handlers[0].level == logging.DEBUG
