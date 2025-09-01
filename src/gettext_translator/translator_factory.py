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

from gettext_translator_service import load_plugins


class TranslatorFactory:
    @staticmethod
    def create_translator(settings):
        plugins = load_plugins()
        if settings.backend in plugins:
            impl_cls = plugins[settings.backend]
            return impl_cls(settings)
        else:
            raise ValueError("Unknown translation backend")
# TranslatorFactory
