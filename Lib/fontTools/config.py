"""
Define all configuration options that can affect the working of fontTools
modules. E.g. optimization levels of varLib IUP, otlLib GPOS compaction, etc.

An instance of the Config class can be attached to a TTFont object, so that
the various modules can access their configuration options from it.

This file lists all the available options, their default values and help text.
"""

from textwrap import dedent
from typing import Any, Callable, Dict, NamedTuple, Union


class Option(NamedTuple):
    name: str
    help: str
    default: Any
    # Turn input (e.g. string) into proper type
    parse: Callable
    # Return true if the parsed value is an acceptable value
    validate: Callable


_OPTIONS_ARRAY = [
    Option(
        name="otlLib.optimize.gpos.mode",
        help=dedent(
            """\
            GPOS Lookup type 2 (PairPos) compaction mode:
                0 = do not attempt to compact PairPos lookups;
                1 to 8 = create at most 1 to 8 new subtables for each existing
                    subtable, provided that it would yield a 50%% file size saving;
                9 = create as many new subtables as needed to yield a file size saving.
            Default: 0.

            This compaction aims to save file size, by splitting large class
            kerning subtables (Format 2) that contain many zero values into
            smaller and denser subtables. It's a trade-off between the overhead
            of several subtables versus the sparseness of one big subtable.

            See the pull request: https://github.com/fonttools/fonttools/pull/2326
            """
        ),
        default=0,
        parse=int,
        validate=lambda v: v in range(10),
    )
]

OPTIONS = {option.name: option for option in _OPTIONS_ARRAY}

_USE_GLOBAL_DEFAULT = object()


class Config:
    _values: Dict

    def __init__(self, values: Dict):
        self._values = {}
        for key, value in values.items():
            option = OPTIONS[key]
            value = option.parse(value)
            if not option.validate(value):
                raise ValueError
            self._values[key] = value

    def get(self, option: Union[Option, str], default=_USE_GLOBAL_DEFAULT):
        """
        Get the value of an option. The value which is returned is the first
        provided among:
        1. a user-provided value in the options's `self.values` dict
        2. a caller-provided default value to this method call
        3. the global default for the option provided in `fontTools.config`

        This is to provide the ability to migrate progressively from config
        options passed as arguments to fontTools APIs to config options read
        from the current TTFont, e.g.

            def fontToolsAPI(font, some_config_option):
                value = font.config.get('someLib.module.some_config_option', some_config_option)
                # use value

        That way, the function will work the same for users of the API that
        still pass the option to the function call, but will favour the new
        config mechanism if the given font specifies a value for that option.

        The config object can be indexed either by string directly or by Option
        object, so that modules can avoid typos in the option name, e.g.

            # Top of someLib.module
            from fontTools.config import OPTIONS
            SOME_OPTION = OPTIONS['someLib.module.some_option']

            # Later in the code
            ttFont.config.get(SOME_OPTION)
        """
        name = getattr(option, "name", option)
        if name in self._values:
            return self._values[name]
        if default is not _USE_GLOBAL_DEFAULT:
            return default
        return OPTIONS[name].default
