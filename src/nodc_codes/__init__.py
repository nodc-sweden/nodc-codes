from nodc_config import Config

from nodc_codes.translate_codes import TranslateCodes


def get_translate_codes_object(nodc_conf: Config) -> TranslateCodes:
    path = nodc_conf.get_path("translate_codes.txt")
    if path is None:
        raise FileNotFoundError("nodc-config path 'translate_codes.txt' not found")
    return TranslateCodes(path)


def get_data_type_list(nodc_conf: Config, translated_to: str = "short_name") -> list[str]:
    return get_translate_codes_object(nodc_conf).get_list(
        "delivery_datatype", translated_to=translated_to
    )


def get_project_list(nodc_conf: Config, translated_to: str = "short_name") -> list[str]:
    return get_translate_codes_object(nodc_conf).get_list("project",
                                                          translated_to=translated_to)


def get_labo_list(nodc_conf: Config, translated_to: str = "short_name") -> list[str]:
    return get_translate_codes_object(nodc_conf).get_list("LABO",
                                                          translated_to=translated_to)

