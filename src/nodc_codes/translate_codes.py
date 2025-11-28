import logging
import pathlib
import polars as pl

logger = logging.getLogger(__name__)


class TranslateCodes:
    def __init__(self, path: str | pathlib.Path, **kwargs):
        self._path = pathlib.Path(path)
        self._encoding = kwargs.get("encoding", "cp1252")

        self._data: pl.DataFrame = pl.DataFrame()
        self._load_file()

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @property
    def internal_keys(self) -> list[str]:
        return sorted(set(self._data["internal_key"]))

    def _load_file(self) -> None:
        self._data = pl.read_csv(self._path, separator="\t", encoding=self._encoding)
        self._data = self._data.fill_null("").with_columns(
            pl.col("synonyms").str.split(by="<or>")
        )

        self._data = self._data.with_columns(
            pl.col("synonyms").list.concat(
                pl.col("internal_value").cast(pl.List(pl.Utf8))
            )
        )

        self._data = self._data.with_columns(
            pl.col("synonyms").list.concat(pl.col("short_name").cast(pl.List(pl.Utf8)))
        )

        self._data = self._data.with_columns(
            pl.col("synonyms").list.concat(
                pl.col("swedish_name").cast(pl.List(pl.Utf8))
            )
        )

        self._data = self._data.with_columns(
            pl.col("synonyms").list.concat(
                pl.col("english_name").cast(pl.List(pl.Utf8))
            )
        )

    def get_internal_value_list(self, internal_key: str) -> list[str]:
        return self._data.filter(pl.col("internal_value") == internal_key)[
            "internal_value"
        ].to_list()

    def get_info(self, internal_key: str = None, synonym: str = None) -> dict | None:
        res = self._data.filter(
            pl.col("internal_key") == internal_key,
            pl.col("synonyms").list.contains(synonym),
        ).to_dicts()
        if not res:
            return {}
        if len(res) > 1:
            raise ValueError(f"To many matches for {internal_key}: {synonym}")
        return res[0]

    def get_list(self, internal_key: str, translated_to: str = "short_name"):
        return sorted(
            set(
                self._data.filter(pl.col("internal_key") == internal_key)[
                    translated_to
                ].to_list()
            )
        )


class TranslateCodesOld:
    def __init__(self, path: str | pathlib.Path, **kwargs):
        self._path = pathlib.Path(path)
        self._encoding = kwargs.get("encoding", "cp1252")

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
    def internal_keys(self) -> list[str]:
        return sorted(self._data)

    @property
    def keys_not_as_synonyms(self) -> list[str]:
        return ["internal_key", "synonyms"]

    @staticmethod
    def _convert_synonym(synonym: str) -> str:
        return synonym
        # return synonym.lower().replace(' ', '')

    @staticmethod
    def _convert_internal_key(internal_key: str) -> str:
        return internal_key
        # return internal_key.lower()

    @staticmethod
    def _convert_internal_value(internal_value: str) -> str:
        return internal_value
        # return internal_value.upper()

    @staticmethod
    def _convert_header_col(header_col: str) -> str:
        return header_col.strip().lower()

    def _load_file(self) -> None:
        header = []
        len_header = None
        with open(self.path, encoding=self._encoding) as fid:
            for r, line in enumerate(fid):
                line = line.strip()
                if not line:
                    continue
                line = line.lstrip("#")
                # if line.startswith('#'):
                #     continue
                split_line = [item.strip() for item in line.split("\t")]
                if r == 0:
                    header = split_line
                    len_header = len(header)
                    self._header = [self._convert_header_col(item) for item in header]
                    continue
                len_split_line = len(split_line)
                if len_split_line < len_header:
                    add_nr = len_header - len_split_line
                    split_line.extend([""] * add_nr)
                line_dict = dict(zip(header, split_line))
                internal_key = self._convert_internal_key(line_dict["internal_key"])

                # Fix synonyms
                line_dict["synonyms"] = set(
                    [
                        self._convert_synonym(item)
                        for item in line_dict["synonyms"].split("<or>")
                    ]
                )
                for col in self.header:
                    if col in self.keys_not_as_synonyms:
                        continue
                    line_dict["synonyms"].add(self._convert_synonym(line_dict[col]))
                line_dict["synonyms"] = [item for item in line_dict["synonyms"] if item]

                # Store synonyms
                self._synonyms.setdefault(internal_key, {})
                for syn in line_dict["synonyms"]:
                    self._synonyms[internal_key][syn] = line_dict["internal_value"]

                # Store data
                self._data.setdefault(internal_key, {})
                self._data[internal_key][
                    self._convert_internal_value(line_dict["internal_value"])
                ] = line_dict

    def get_internal_value_list(self, internal_key: str) -> list[str]:
        return sorted(self._data[self._convert_internal_key(internal_key)])

    def get_internal_value(
        self, internal_key: str = None, synonym: str = None
    ) -> str | None:
        return self._synonyms.get(self._convert_internal_key(internal_key), {}).get(
            self._convert_synonym(synonym), None
        )

    def get_info(self, internal_key: str = None, synonym: str = None) -> dict | None:
        internal_value = self.get_internal_value(internal_key, synonym)
        if not internal_value:
            return None
        return self._data[self._convert_internal_key(internal_key)][
            self._convert_internal_value(internal_value)
        ]

    def get_translation(
        self,
        internal_key: str = None,
        synonym: str = None,
        translate_to: str = None,
        field: str = None,
    ) -> str | None:
        if field:
            internal_key = field
        translate_to = self._convert_header_col(translate_to)
        if translate_to not in self.header:
            logger.warning(
                f'Not able to translate to "{translate_to}". Nu such mapping available'
            )
            return None
        internal_value = self.get_internal_value(internal_key, synonym)
        if not internal_value:
            logger.warning(
                f'Could not find internal_value matching "{synonym}" in internal_key "{internal_key}"'
            )
            return None
        return self._data[self._convert_internal_key(internal_key)][
            self._convert_internal_value(internal_value)
        ][translate_to]

    def list_synonyms(self, internal_key: str, internal_value: str) -> list[str]:
        internal_key = self._convert_internal_key(internal_key)
        internal_value = self._convert_internal_value(internal_value)
        return self._data[internal_key][internal_value]["synonyms"]

    def get_swedish_name(
        self, internal_key: str = None, synonym: str = None
    ) -> str | None:
        return self.get_translation(
            internal_key=internal_key, synonym=synonym, translate_to="swedish_name"
        )

    def get_english_name(self, internal_key: str, synonym: str) -> str | None:
        return self.get_translation(
            internal_key=internal_key, synonym=synonym, translate_to="english_name"
        )
