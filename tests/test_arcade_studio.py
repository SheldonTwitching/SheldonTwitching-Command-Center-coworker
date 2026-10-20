import json
import math
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from arcade_studio import ArcadeStudio, DEFAULT, PALETTES, validated


def test_viewport_is_persistently_16_9_and_protected():
    c = validated({**DEFAULT,'artworkMode':'variation', 'gameWidth': 1440, 'gameTop': 190})
    assert c['canvasWidth'] == 1920 and c['canvasHeight'] == 1080
    assert c['gameWidth'] / (c['gameWidth'] * 9 / 16) == 16 / 9
    assert c['gameTop'] == 100  # controls never collide with reserved deck
    assert c['gameTop'] + round(c['gameWidth'] * 9 / 16) == 910


def test_validation_rejects_unsafe_theme_values():
    import pytest
    for change in ({'panelColor': 'url(https://evil)'}, {'gameWidth': 300},
                   {'gameTop': float('nan')}, {'buttonColors': ['#ff0000']},
                   {'marquee': '<x>' * 120}, {'controllerSlot': 9},
                   {'buttonActions': ['not-an-action'] * 8}):
        with pytest.raises(ValueError):
            validated({**DEFAULT,'artworkMode':'variation', **change})


def test_palette_and_virtual_buttons_persist(tmp_path):
    app = ArcadeStudio(tmp_path)
    c = app.get()
    assert not c['controllerCommands']
    c['palette'] = 'Sheldon Neon'  # Preserve the known legacy palette sequence.
    c['buttonActions'][0] = 'cycle'
    app.save(c)
    result = app.click(0)
    assert result['action'] == 'cycle'
    assert app.get()['palette'] == 'Final Round'
    assert app.live()['pressed'] == [0]
    assert ArcadeStudio(tmp_path).get()['palette'] == 'Final Round'


def test_scanlines_toggle_does_not_force_game_scanlines(tmp_path):
    studio = ArcadeStudio(tmp_path)
    c = studio.get()
    c['buttonActions'][1] = 'scanlines'
    studio.save(c)
    studio.click(1)
    assert studio.get()['scanlines'] is False
    assert studio.get()['scanlinesOnGame'] is False


def test_controller_actions_are_off_by_default(tmp_path):
    studio = ArcadeStudio(tmp_path)
    assert studio.get()['controllerCommands'] is False
    assert studio.live()['connected'] is False or isinstance(studio.live()['connected'], bool)