"""Unit tests for AppSettings persistence."""

from pathlib import Path

from src.core import AppSettings, load_settings, save_settings


def test_settings_roundtrip_and_fallback(tmp_path: Path) -> None:
    cfg = tmp_path / "settings.json"
    assert load_settings(cfg) == AppSettings()

    custom = AppSettings(
        board_theme="warm_wood",
        piece_style="minimal",
        animation_speed="slow",
    )
    save_settings(custom, cfg)
    assert load_settings(cfg) == custom

    cfg.write_text("{corrupt json", encoding="utf-8")
    assert load_settings(cfg) == AppSettings()
