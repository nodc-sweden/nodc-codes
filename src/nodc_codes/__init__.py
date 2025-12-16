import functools
import logging
import os
import pathlib

from nodc_codes.translate_codes import TranslateCodes


def get_user_given_config_dir() -> pathlib.Path | None:
    path = pathlib.Path(os.getcwd()) / "config_directory.txt"
    if not path.exists():
        return
    with open(path) as fid:
        config_path = fid.readline().strip()
        if not config_path:
            return
        config_path = pathlib.Path(config_path)
        if not config_path.exists():
            return
        return config_path


logger = logging.getLogger(__name__)

CONFIG_ENV = "NODC_CONFIG"

home = pathlib.Path.home()
OTHER_CONFIG_SOURCES = [
    home / "NODC_CONFIG",
    home / ".NODC_CONFIG",
    home / "nodc_config",
    home / ".nodc_config",
]

CONFIG_FILE_NAMES = ["translate_codes.txt"]


CONFIG_DIRECTORY = None
conf_dir = get_user_given_config_dir()
if conf_dir:
    CONFIG_DIRECTORY = conf_dir
else:
    if os.getenv(CONFIG_ENV) and pathlib.Path(os.getenv(CONFIG_ENV)).exists():
        CONFIG_DIRECTORY = pathlib.Path(os.getenv(CONFIG_ENV))
    else:
        for directory in OTHER_CONFIG_SOURCES:
            if directory.exists():
                CONFIG_DIRECTORY = directory
                break


def get_config_path(name: str = None) -> pathlib.Path:
    if not CONFIG_DIRECTORY:
        raise NotADirectoryError(
            f"Config directory not found. Environment path {CONFIG_ENV} does not seem to be set and not other config directory was found. "
        )
    if name not in CONFIG_FILE_NAMES:
        raise FileNotFoundError(f'No config file with name "{name}" exists')
    path = CONFIG_DIRECTORY / name
    if not path.exists():
        raise FileNotFoundError(f"Could not find config file {name}")
    return path


@functools.cache
def get_translate_codes_object() -> TranslateCodes:
    path = get_config_path("translate_codes.txt")
    return TranslateCodes(path)


def get_data_type_list(translated_to: str = "short_name") -> list[str]:
    return get_translate_codes_object().get_list(
        "delivery_datatype", translated_to=translated_to
    )


def get_project_list(translated_to: str = "short_name") -> list[str]:
    return get_translate_codes_object().get_list("project", translated_to=translated_to)


def get_labo_list(translated_to: str = "short_name") -> list[str]:
    return get_translate_codes_object().get_list("LABO", translated_to=translated_to)


if __name__ == "__main__":
    codes = get_translate_codes_object()
