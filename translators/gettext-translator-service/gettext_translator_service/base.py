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


class TranslatorService(ABC):
    REQUIRES_CONFIG: list[str]

    @abstractmethod
    def __init__(self) -> None:
        pass
    # __init__

    @abstractmethod
    def configure(self):
        pass
    # configure

    @abstractmethod
    def translate(self, texts):
        '''Translates one or more strings, depending on the backend'''
        pass
    # translate

    # -------------------------------------------------------------------------

    def get_required_configuration(self):
        meta = {}
        for name, typ in self.__annotations__.items():
            value = getattr(self, name, None)
            meta[name] = value

        return meta
    # get_required_configuration
# TranslatorService
