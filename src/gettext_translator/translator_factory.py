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

from gettext_translator_service import load_plugins


class TranslatorFactory:
    @staticmethod
    def create_translator(settings):
        plugins = load_plugins()
        if settings.backend in plugins:
            impl_cls = plugins[settings.backend]
            return impl_cls(settings)
        else:
            raise ValueError("❌ Unknown translation backend")
# TranslatorFactory
