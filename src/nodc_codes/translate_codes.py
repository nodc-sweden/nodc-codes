import logging
import pathlib

logger = logging.getLogger(__name__)


class TranslateCodes:

    def __init__(self, path: str | pathlib.Path, **kwargs):
        self._path = pathlib.Path(path)
        self._encoding = kwargs.get('encoding', 'cp1252')

        self._header = []
        self._data = dict()
        self._synonyms = dict()

        self._load_file()

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @property
    def header(self) -> list[str]:
        return self._header

    @property
    def fields(self) -> list[str]:
        return sorted(self._data)

    @property
    def keys_not_as_synonyms(self) -> list[str]:
        return ['filed', 'filter', 'source', 'synonyms']

    @staticmethod
    def _convert_synonym(synonym: str) -> str:
        return synonym.lower().replace(' ', '')

    @staticmethod
    def _convert_field(field: str) -> str:
        return field.lower()

    @staticmethod
    def _convert_public_value(public_value: str) -> str:
        return public_value.upper()

    @staticmethod
    def _convert_header_col(header_col: str) -> str:
        return header_col.strip().lower()

    def _load_file(self) -> None:
        header = []
        with open(self.path) as fid:
            for r, line in enumerate(fid):
                if not line.strip():
                    continue
                split_line = [item.strip() for item in line.split('\t')]
                if r == 0:
                    header = split_line
                    self._header = [self._convert_header_col(item) for item in header]
                    continue
                line_dict = dict(zip(header, split_line))
                field = self._convert_field(line_dict['field'])

                # Fix synonyms
                line_dict['synonyms'] = set([self._convert_synonym(item) for item in line_dict['synonyms'].split('<or>')])
                for col in self.header:
                    if col in self.keys_not_as_synonyms:
                        continue
                    line_dict['synonyms'].add(self._convert_synonym(line_dict[col]))

                # Store synonyms
                self._synonyms.setdefault(field, {})
                for syn in line_dict['synonyms']:
                    self._synonyms[field][syn] = line_dict['public_value']

                # Store data
                self._data.setdefault(field, {})
                self._data[field][self._convert_public_value(line_dict['public_value'])] = line_dict

    def get_public_value_list(self, field: str) -> list[str]:
        return sorted(self._data[self._convert_field(field)])

    def get_public_value(self, field: str = None, synonym: str = None) -> str | None:
        return self._synonyms.get(self._convert_field(field), {}).get(self._convert_synonym(synonym), None)

    def get_info(self, field: str = None, synonym: str = None) -> dict | None:
        public_value = self.get_public_value(field, synonym)
        if not public_value:
            return None
        return self._data[field][self._convert_public_value(public_value)]

    # def get_swedish_name(self, field: str = None, synonym: str = None) -> str | None:
    #     public_value = self.get_public_value(field, synonym)
    #     if not public_value:
    #         return None
    #     return self._data[field][self._convert_public_value(public_value)]['swedish_name']
    #
    # def get_english_name(self, field: str = None, synonym: str = None) -> str | None:
    #     public_value = self.get_public_value(field, synonym)
    #     if not public_value:
    #         return None
    #     return self._data[field][self._convert_public_value(public_value)]['english_name']

    def get_translation(self, field: str = None, synonym: str = None, translate_to: str = None) -> str | None:
        translate_to = self._convert_header_col(translate_to)
        if translate_to not in self.header:
            logger.warning(f'Not able to translate to "{translate_to}". Nu such mapping available')
            return None
        public_value = self.get_public_value(field, synonym)
        if not public_value:
            logger.warning(f'Could not find public_value matching "{synonym}" in field "{field}"')
            return None
        return self._data[field][self._convert_public_value(public_value)][translate_to]

    def list_synonyms(self, field: str, public_value: str) -> list[str]:
        field = self._convert_field(field)
        public_value = self._convert_public_value(public_value)
        return self._data[field][public_value]['synonyms']

