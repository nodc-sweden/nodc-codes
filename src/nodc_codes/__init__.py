import functools
import logging
import pathlib

import requests
import ssl

from .translate_codes import TranslateCodes

logger = logging.getLogger(__name__)


THIS_DIR = pathlib.Path(__file__).parent
CONFIG_DIR = THIS_DIR / 'CONFIG_FILES'

CONFIG_URLS = [
    r'https://raw.githubusercontent.com/nodc-sweden/nodc-codes/main/src/nodc_codes/CONFIG_FILES/translate_codes.txt',
]


@functools.cache
def get_translate_codes_object() -> "TranslateCodes":
    path = CONFIG_DIR / 'translate_codes.txt'
    return TranslateCodes(path)


def update_config_files() -> None:
    """Downloads config files from github"""
    try:
        for url in CONFIG_URLS:
            name = pathlib.Path(url).name
            target_path = CONFIG_DIR / name
            res = requests.get(url, verify=ssl.CERT_NONE)
            with open(target_path, 'w', encoding='utf8') as fid:
                fid.write(res.text)
                logger.info(f'Config file "{name}" updated from {url}')
    except requests.exceptions.ConnectionError:
        logger.warning('Connection error. Could not update config files!')
        raise

