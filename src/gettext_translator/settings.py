"""
    AI-based Gettext automatic translator.
    Copyright (C) 2026 Rodolfo González González.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# -----------------------------------------------------------------------------


import argparse
import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import (
    PydanticBaseSettingsSource
)
from pydantic import Field, field_validator, model_validator
from typing import Any, Dict, Self, Tuple
from langcodes import Language

# -----------------------------------------------------------------------------


class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls, yaml_file: str = None):
        super().__init__(settings_cls)
        self.yaml_file = yaml_file
        self._yaml_data = {}

        if yaml_file:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    self._yaml_data = yaml.safe_load(f) or {}
            except (FileNotFoundError, yaml.YAMLError):
                self._yaml_data = {}

    def get_field_value(self, field_info, field_name: str) -> Tuple[Any, str, bool]:
        value = self._yaml_data.get(field_name)
        if value is None:
            return None, field_name, False
        return value, field_name, True

    def prepare_field_value(self, field_name: str, value: Any, value_origin: Any) -> Any:
        return value

    def __call__(self) -> Dict[str, Any]:
        return self._yaml_data
# YamlConfigSettingsSource

# -----------------------------------------------------------------------------


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="allow",
    )

    # -------------------------------------------------------------------------

    info: bool = Field(default=False)
    backend: str = Field(default="")
    po: str = Field(default="")
    src: str = Field(default=Language.make(language='en').language)
    dst: str = Field(default=Language.make(language='en').language)
    fuzzy: bool = Field(default=True)
    ascribe: bool = Field(default=False)
    config: str = Field(default="config.yaml")

    # -------------------------------------------------------------------------

    @field_validator('po')
    @classmethod
    def validate_po(cls, v, info):
        if info.data.get('info'):
            return v  # Skip validation if info is present
        if not v:
            raise ValueError('po must be provided unless --info are used.')
        return v
    # validate_po

    # -------------------------------------------------------------------------

    @field_validator("src", "dst")
    @classmethod
    def validate_iso639(cls, v, info):
        if Language.get(v).is_valid():
            return Language.get(v).maximize()
        raise ValueError("invalid language code")
    # validate_iso639

    # -------------------------------------------------------------------------

    @model_validator(mode='after')
    def validar_info_backend(self) -> Self:
        if self.info and not self.backend:
            raise ValueError("please tell me which backend do you want to see information about")
        return self
    # validar_info_backend

    # -------------------------------------------------------------------------

    @classmethod
    def parse_cli_args(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument("--info", action='store_true', help="Shows information about the backend")
        parser.add_argument("--backend", type=str, help="Which backend to use")
        parser.add_argument("--po", type=str, help="The path to the .po file")
        parser.add_argument("--src", type=str, default=Language.make(language='en').language, help="The source language")
        parser.add_argument("--dst", type=str, help="The language to translate to")
        parser.add_argument("--fuzzy", type=lambda x: x.lower() in ["true", "1", "yes"], help="Fuzzy translations?")
        parser.add_argument("--ascribe", default=False, type=lambda x: x.lower() in ["true", "1", "yes"],
                            help="Include a comment in each entry indicating that it was translated with AI")
        parser.add_argument("--config", type=str, default="config.yaml", required=False, help="Path to the .yaml configuration file for the backend.")
        args = parser.parse_args()
        return args
    # parse_cli_args

    # -------------------------------------------------------------------------

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings: PydanticBaseSettingsSource,
        **kwargs
    ):
        cli_args = cls.parse_cli_args()
        yaml_source = YamlConfigSettingsSource(settings_cls, getattr(cli_args, 'config', None))

        return (
            yaml_source,     # YAML
            init_settings,   # CLI args
        )
    # settings_customise_sources
# Settings
