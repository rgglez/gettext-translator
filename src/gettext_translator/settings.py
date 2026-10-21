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
import os
import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import (
    PydanticBaseSettingsSource
)
from pydantic import Field, field_validator, model_validator
from typing import Any, Dict, Self, Tuple
from langcodes import Language
from .version import __version__

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
            except FileNotFoundError:
                self._yaml_data = {}

        # Values like "env:MY_VAR" are read from the environment variable MY_VAR
        for key, value in self._yaml_data.items():
            if isinstance(value, str) and value.startswith("env:"):
                self._yaml_data[key] = os.getenv(value[len("env:"):])

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
    po: list[str] = Field(default_factory=list)
    src: str = Field(default=Language.make(language='en').language)
    dst: str = Field(default=Language.make(language='en').language)
    fuzzy: bool = Field(default=False)
    context: str = Field(default="")
    verbose: str = Field(default="warning")
    ascribe: bool = Field(default=False)
    config: str = Field(default="config.yaml")
    dry_run: bool = Field(default=False)
    output: str = Field(default="")
    cache: str = Field(default="")

    # -------------------------------------------------------------------------

    @field_validator('po')
    @classmethod
    def validate_po(cls, v, info):
        if info.data.get('info'):
            return v  # Skip validation if info is present
        if not v:
            raise ValueError('po must be provided unless --info is used.')
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
    def validate_info_backend(self) -> Self:
        if self.info and not self.backend:
            raise ValueError("please tell me which backend do you want to see information about")
        return self
    # validate_info_backend

    # -------------------------------------------------------------------------

    @classmethod
    def parse_cli_args(cls, argv=None):
        # Only the arguments given in the command line are returned, so the
        # YAML file and the field defaults can fill in the rest
        parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
        parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
        parser.add_argument("--info", action='store_true',
                            help="Shows information about the backend")
        parser.add_argument("--backend", type=str,
                            help="Which backend to use")
        parser.add_argument("--po", type=str, nargs="+",
                            help="The .po file(s) or directories containing .po files")
        parser.add_argument("--src", type=str,
                            help="The source language. Default: en")
        parser.add_argument("--dst", type=str,
                            help="The language to translate to")
        parser.add_argument("--fuzzy", action='store_true',
                            help="Remove the fuzzy flag from all entries before translating")
        parser.add_argument("--context", type=str,
                            help="Optional default translation context for msgid without msgctxt")
        parser.add_argument("--verbose", type=str.lower,
                            choices=["debug", "info", "warning", "error", "critical"],
                            help="Logging level. Default: warning")
        parser.add_argument("--ascribe", action='store_true',
                            help="Include a comment in each entry indicating that it was translated with AI")
        parser.add_argument("--config", type=str,
                            help="Path to the .yaml configuration file for the backend. Default: config.yaml")
        parser.add_argument("--dry-run", action='store_true',
                            help="Show the translations without saving any file")
        parser.add_argument("--output", type=str,
                            help="Save to this .po file (single input) or directory, instead of overwriting the input")
        parser.add_argument("--cache", type=str,
                            help="Path to a SQLite file used to cache translations between runs")
        return parser.parse_args(argv)
    # parse_cli_args

    # -------------------------------------------------------------------------

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings: PydanticBaseSettingsSource,
        **kwargs
    ):
        config_file = init_settings.init_kwargs.get('config', cls.model_fields['config'].default)
        yaml_source = YamlConfigSettingsSource(settings_cls, config_file)

        return (
            init_settings,   # CLI args
            yaml_source,     # YAML
        )
    # settings_customise_sources
# Settings
