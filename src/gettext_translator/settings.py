"""
Copyright 2025 Rodolfo González González

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# -----------------------------------------------------------------------------


import argparse
import json
import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import (
    PydanticBaseSettingsSource,
    DotEnvSettingsSource
)
from pydantic import Field, field_validator
from typing import Any, Dict, Tuple
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
        env_file=".env"
    )

    # -------------------------------------------------------------------------

    backend: str = Field(default="")
    info: bool = Field(default=False)
    plugin_options: str = Field(default="")
    po: str = Field(default="")
    src: str = Field(default=Language.make(language='en').language)
    dst: str = Field(default=Language.make(language='en').language)
    fuzzy: bool = Field(default=True)
    config: str = Field(default="")

    # -------------------------------------------------------------------------

    @field_validator('backend')
    @classmethod
    def validate_backend(cls, v, info):
        if not v:
            raise ValueError('backend must be provided.')
        return v
    # validate_backend

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

    @field_validator("plugin_options")
    @classmethod
    def validate_plugin_options(cls, v, info):
        if info.data.get('info'):
            return v  # Skip validation if info is present
        try:
            if v:
                json_object = json.loads(v)
            else:
                json_object = json.loads('{}')
            return json_object
        except ValueError:
            raise ValueError("plugin_options is not a valid json string")
    # validate_plugin_options

    # -------------------------------------------------------------------------

    @classmethod
    def parse_cli_args(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument("--info", action='store_true', help="Shows information about the backend")
        parser.add_argument("--backend", type=str, help="The backend plugin to use")
        parser.add_argument("--plugin_options", type=str, help="The particular options for the used plugin")
        parser.add_argument("--po", type=str, help="The path to the .po file")
        parser.add_argument("--src", type=str, default=Language.make(language='en').language, help="The source language")
        parser.add_argument("--dst", type=str, help="The language to translate to")
        parser.add_argument("--fuzzy", type=lambda x: x.lower() in ["true", "1", "yes"], help="Fuzzy translations?")
        parser.add_argument("--config", type=str, default="config.yaml", help="Path to the .yaml config file (optional, takes presedence)")
        args = parser.parse_args()
        return args
    # parse_cli_args

    # -------------------------------------------------------------------------

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
        **kwargs  # This handles version differences
    ):
        # Handle both possible parameter names
        env_source = kwargs.get('env_settings') or kwargs.get('dotenv_settings')
        cli_args = cls.parse_cli_args()

        dotenv_source = DotEnvSettingsSource(settings_cls, env_file=".env", env_file_encoding="utf-8")
        yaml_source = YamlConfigSettingsSource(settings_cls, getattr(cli_args, 'config', None))

        return (
            yaml_source,     # 1 YAML
            dotenv_source,   # 2 .env
            env_source,      # 3 Environment variables
            init_settings,   # 4 CLI args
        )
    # settings_customise_sources
# Settings
