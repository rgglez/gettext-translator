"""
Gettext Translator

This Python script provides a tool for translating gettext .po files
using OpenAI's API, Microsoft Azure Translator or local AI models.
It is designed to handle both bulk and individual translation modes.

---

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

# -------------------------------------------------------------------------


import argparse
from enum import Enum
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import (
    PydanticBaseSettingsSource,
    DotEnvSettingsSource
)
from pydantic import Field, field_validator
import yaml
from typing import Any, Dict, Tuple

# -------------------------------------------------------------------------


class BackendEnum(str, Enum):
    azure = "azure"
    chatgpt = "chatgpt"
    marianmt = "marianmt"
# BackendEnum

# -------------------------------------------------------------------------


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

# -------------------------------------------------------------------------


class MySettings(BaseSettings):
    model_config = SettingsConfigDict(
        extra="allow",
        env_file=".env"
    )

    backend: BackendEnum
    apikey: str = Field(default="")
    model: str = Field(default="")
    location: str = Field(default="")
    po: str
    src: str
    dst: str
    fuzzy: bool = Field(default=True)
    bulk: bool = Field(default=True)
    bulksize: int = Field(default=49500)
    config: str = Field(default="")

    @field_validator("src", "dst")
    @classmethod
    def validate_iso639(cls, v):
        if not (len(v) == 2 and v.isalpha()):
            raise ValueError(f"Invalid ISO 639 code: {v}")
        return v.lower()

    @field_validator("apikey")
    @classmethod
    def validate_apikey(cls, v, info):
        backend = info.data.get("backend")
        if backend in {"azure", "chatgpt"} and not v:
            raise ValueError(f"apikey is required for backend={backend}")
        return v

    @field_validator("model")
    @classmethod
    def validate_model(cls, v, info):
        if info.data.get("backend") == "chatgpt" and not v:
            raise ValueError("model is required for backend=chatgpt")
        return v

    @field_validator("location")
    @classmethod
    def validate_location(cls, v, info):
        if info.data.get("backend") == "azure" and not v:
            raise ValueError("location is required for backend=azure")
        return v

    @classmethod
    def parse_cli_args(cls):
        parser = argparse.ArgumentParser()
        parser.add_argument("--backend", type=str)
        parser.add_argument("--apikey", type=str)
        parser.add_argument("--model", type=str)
        parser.add_argument("--location", type=str)
        parser.add_argument("--po", type=str)
        parser.add_argument("--src", type=str)
        parser.add_argument("--dst", type=str)
        parser.add_argument("--fuzzy", type=lambda x: x.lower() in ["true", "1", "yes"])
        parser.add_argument("--bulk", type=lambda x: x.lower() in ["true", "1", "yes"])
        parser.add_argument("--bulksize", type=int)
        parser.add_argument("--config", type=str, default="config.yaml", help="Ruta al archivo YAML")
        args = parser.parse_args()
        return args
    # parse_cli_args

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
# MySettings
