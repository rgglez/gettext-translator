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

from abc import ABC, abstractmethod

# -----------------------------------------------------------------------------


class Capabilities:
    def __init__(self, description: str, supports_single: bool, supports_batch: bool, is_cloud: bool):
        self.description = description
        self.supports_single = supports_single
        self.supports_batch = supports_batch
        self.is_cloud = is_cloud
    # __init__

    def to_dict(self) -> dict:
        """Convert the capabilities to a dictionary."""
        return {
            "description": self.description,
            "supports_single": self.supports_single,
            "supports_batch": self.supports_batch,
            "is_cloud": self.is_cloud
        }
    # to_dict
# Capabilities

# -----------------------------------------------------------------------------


class TranslatorService(ABC):
    @abstractmethod
    def __init__(self) -> None:
        pass
    # __init__

    @abstractmethod
    def get_capabilities(self) -> Capabilities:
        """Return an instance of Capabilities for the plugin."""
        pass
    # get_capabilities

    @abstractmethod
    def translate_batch(self, texts):
        pass
    # translate_batch

    @abstractmethod
    def translate(self, texts):
        pass
    # translate
# TranslatorService
