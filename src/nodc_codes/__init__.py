import functools
import pathlib
import sys

from .translate_codes import TranslateCodes


if getattr(sys, 'frozen', False):
    THIS_DIR = pathlib.Path(sys.executable).parent
else:
    THIS_DIR = pathlib.Path(__file__).parent

CONFIG_DIR = THIS_DIR.parent / 'CONFIG_FILES'

if not CONFIG_DIR.exists():
    CONFIG_DIR = THIS_DIR / 'CONFIG_FILES'


@functools.cache
def get_translate_codes_object() -> "TranslateCodes":
    path = CONFIG_DIR / 'translate_codes_NEW.txt'
    return TranslateCodes(path)