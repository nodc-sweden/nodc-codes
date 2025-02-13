import functools
import logging
import os
import pathlib

from nodc_codes.translate_codes import TranslateCodes

logger = logging.getLogger(__name__)

CONFIG_ENV = 'NODC_CONFIG'

CONFIG_FILE_NAMES = [
    'translate_codes.txt'
]


CONFIG_DIRECTORY = None
if os.getenv(CONFIG_ENV) and pathlib.Path(os.getenv(CONFIG_ENV)).exists():
    CONFIG_DIRECTORY = pathlib.Path(os.getenv(CONFIG_ENV))


def get_config_path(name: str) -> pathlib.Path:
    if not CONFIG_DIRECTORY:
        raise NotADirectoryError(f'Config directory not found. Environment path {CONFIG_ENV} does not seem to be set.')
    if name not in CONFIG_FILE_NAMES:
        raise FileNotFoundError(f'No config file with name "{name}" exists')
    path = CONFIG_DIRECTORY / name
    if not path.exists():
        raise FileNotFoundError(f'Could not find config file {name}')
    return path


@functools.cache
def get_translate_codes_object() -> "TranslateCodes":
    path = get_config_path('translate_codes.txt')
    return TranslateCodes(path)


if __name__ == '__main__':
    codes = get_translate_codes_object()


