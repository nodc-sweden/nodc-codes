import functools
import logging
import pathlib
import os

import requests
import ssl

from nodc_codes.translate_codes import TranslateCodes

logger = logging.getLogger(__name__)

CONFIG_SUBDIRECTORY = 'nodc_codes'
CONFIG_FILE_NAMES = [
    'translate_codes.txt'
]


CONFIG_DIRECTORY = None
if os.getenv('NODC_CONFIG') and pathlib.Path(os.getenv('NODC_CONFIG')).exists():
    CONFIG_DIRECTORY = pathlib.Path(os.getenv('NODC_CONFIG')) / CONFIG_SUBDIRECTORY
TEMP_CONFIG_DIRECTORY = pathlib.Path.home() / 'temp_nodc_config' / CONFIG_SUBDIRECTORY
TEMP_CONFIG_DIRECTORY.mkdir(exist_ok=True, parents=True)


CONFIG_URL = r'https://raw.githubusercontent.com/nodc-sweden/nodc_config/refs/heads/main/' + f'{CONFIG_SUBDIRECTORY}/'


def get_config_path(name: str) -> pathlib.Path:
    if name not in CONFIG_FILE_NAMES:
        raise FileNotFoundError(f'No config file with name "{name}" exists')
    if CONFIG_DIRECTORY:
        path = CONFIG_DIRECTORY / name
        if path.exists():
            return path
    temp_path = TEMP_CONFIG_DIRECTORY / name
    if temp_path.exists():
        return temp_path
    update_config_file(temp_path)
    if temp_path.exists():
        return temp_path
    raise FileNotFoundError(f'Could not find config file {name}')


def update_config_file(path: pathlib.Path) -> None:
    path.parent.mkdir(exist_ok=True, parents=True)
    url = CONFIG_URL + path.name
    try:
        res = requests.get(url, verify=ssl.CERT_NONE)
        with open(path, 'w', encoding='utf8') as fid:
            fid.write(res.text)
            logger.info(f'Config file "{path.name}" updated from {url}')
    except requests.exceptions.ConnectionError:
        logger.warning(f'Connection error. Could not update config file {path.name}')
        raise


def update_config_files() -> None:
    """Downloads config files from github"""
    for name in CONFIG_FILE_NAMES:
        target_path = TEMP_CONFIG_DIRECTORY / name
        update_config_file(target_path)


@functools.cache
def get_translate_codes_object() -> "TranslateCodes":
    path = get_config_path('translate_codes.txt')
    return TranslateCodes(path)


if __name__ == '__main__':
    update_config_files()


