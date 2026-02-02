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

from abc import ABC, abstractmethod
import inspect
import json
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

# -----------------------------------------------------------------------------


class TranslatorService(ABC):
    REQUIRES_CONFIG: list[str]

    # -------------------------------------------------------------------------

    @abstractmethod
    def __init__(self) -> None:
        pass
    # __init__

    # -------------------------------------------------------------------------

    @abstractmethod
    def configure(self):
        pass
    # configure

    # -------------------------------------------------------------------------

    @abstractmethod
    def translate(self, texts):
        '''Translates one or more strings, depending on the backend'''
        pass
    # translate

    # -------------------------------------------------------------------------

    @classmethod
    def show_info(cls):
        print("\n")
        print("=" * 80)
        print("README file for the plugin:")
        print("=" * 80)
        print("\n")

        """Reads and renders the README.md for the plugin"""
        # Get the file where the caller class (cls) is defined
        class_file = inspect.getfile(cls)
        readme_path = Path(class_file).parent.parent / "README.md"

        # Check if file exists
        if not readme_path.exists():
            print(f"❌ README.md not found in: {readme_path}")
            return

        # Read the README
        contents = readme_path.read_text(encoding='utf-8')

        # Rich console
        console = Console()

        # Render the Markdown
        md = Markdown(contents)
        console.print(md)

        print("\n")
        print("=" * 80)
        print("Required options for the YAML configuration file:")
        print("=" * 80)
        print("\n")

        meta = {}
        for name, typ in cls.__annotations__.items():
            value = getattr(cls, name, None)
            meta[name] = value
        print(json.dumps(meta, indent=2))
    # show_info
# TranslatorService
