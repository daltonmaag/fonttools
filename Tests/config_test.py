import pytest

from fontTools.ttLib import TTFont

def test_ttfont_has_config():
    ttFont = TTFont(config={"otlLib.optimize.gpos.mode": 8})
    assert 8 == ttFont.config.get("otlLib.optimize.gpos.mode")

def test_can_access_config_by_option_object():
    from fontTools.otlLib.optimize.gpos import MODE_OPTION
    ttFont = TTFont(config={"otlLib.optimize.gpos.mode": 8})
    assert 8 == ttFont.config.get(MODE_OPTION)
    assert 8 == ttFont.config.get(MODE_OPTION, 3)

def test_no_config_yields_default_values():
    ttFont = TTFont()
    assert 0 == ttFont.config.get("otlLib.optimize.gpos.mode")
    assert 3 == ttFont.config.get("otlLib.optimize.gpos.mode", 3)

def test_cannot_set_inexistent_key():
    with pytest.raises(KeyError):
        TTFont(config={"notALib.notAModule.inexistent": 4})

def test_value_gets_parsed():
    # Note: value given as a string
    ttFont = TTFont(config={"otlLib.optimize.gpos.mode": "8"})
    assert 8 == ttFont.config.get("otlLib.optimize.gpos.mode")

def test_value_gets_validated():
    # Note: 12 is not a valid value for GPOS compaction mode (must be in 0-9)
    with pytest.raises(ValueError):
        TTFont(config={"otlLib.optimize.gpos.mode": 12})
