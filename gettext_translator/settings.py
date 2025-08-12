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

import os
import yaml
from enum import Enum
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict, PydanticBaseSettingsSource

# -------------------------------------------------------------------------


class BackendEnum(str, Enum):
    azure = "azure"
    chatgpt = "chatgpt"
    marianmt = "marianmt"
# BackendEnum

# -------------------------------------------------------------------------


class Settings(BaseSettings):
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

    model_config = SettingsConfigDict(extra="ignore")

    @field_validator("src", "dst")
    def validate_iso639(cls, v):
        if not (len(v) == 2 and v.isalpha()):
            raise ValueError(f"Invalid ISO 639 code: {v}")
        return v.lower()

    @field_validator("apikey")
    def validate_apikey(cls, v, values):
        backend = values.get("backend")
        if backend in {"azure", "chatgpt"} and not v:
            raise ValueError(f"apikey is required for backend={backend}")
        return v

    @field_validator("model")
    def validate_model(cls, v, values):
        if values.get("backend") == "chatgpt" and not v:
            raise ValueError("model is required for backend=chatgpt")
        return v

    @field_validator("location")
    def validate_location(cls, v, values):
        if values.get("backend") == "azure" and not v:
            raise ValueError("location is required for backend=azure")
        return v
# Settings

# -------------------------------------------------------------------------


class YamlConfigSettingsSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls, yaml_file: str):
        super().__init__(settings_cls)
        self.yaml_file = yaml_file

    def __call__(self):
        if os.path.isfile(self.yaml_file):
            with open(self.yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            return data
        return {}
# YamlConfigSettingsSource
