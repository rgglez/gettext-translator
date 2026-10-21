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
import importlib.metadata
import inspect
import json
from rich.console import Console
from rich.markdown import Markdown

# -----------------------------------------------------------------------------


class TranslatorService(ABC):
    """
    Base class for translation backends.

    Contract of translate():

    Input: a list of items, one per unique string to translate:
        {"n": int, "id": str, "ctx": str (optional),
         "plural": str (optional), "nplurals": int (present when "plural" is)}

    Output: a list of results, in any order, each one referring to its item by "n":
        {"n": int, "msgstr": str}                  for items without "plural"
        {"n": int, "msgstr_plural": [str, ...]}    for items with "plural", nplurals forms

    Items that cannot be translated may be omitted from the output.
    """

    # Options that must be present in the YAML configuration file
    REQUIRES_CONFIG: list[str] = []

    # -------------------------------------------------------------------------

    def __init__(self, settings) -> None:
        self.config = settings

        if not settings.info:
            missing = [k for k in self.REQUIRES_CONFIG if getattr(settings, k, None) in (None, "")]
            if missing:
                raise ValueError(f"Missing option(s) {', '.join(missing)} in configuration file {settings.config}")
    # __init__

    # -------------------------------------------------------------------------

    def configure(self):
        """Connects to the service or loads the model. Called once before translate()."""
    # configure

    # -------------------------------------------------------------------------

    @abstractmethod
    def translate(self, items: list[dict]) -> list[dict]:
        """Translates the items, see the class docstring for the contract."""
    # translate

    # -------------------------------------------------------------------------

    @classmethod
    def show_info(cls):
        """Renders the README of the plugin (from its package metadata) and its required options."""
        module = inspect.getmodule(cls).__name__.split(".")[0]
        dists = importlib.metadata.packages_distributions().get(module, [])
        readme = importlib.metadata.metadata(dists[0]).get_payload() if dists else ""

        console = Console()
        console.rule("README file for the plugin")
        console.print(Markdown(readme) if readme else f"❌ No README found for {module}")
        console.rule("Required options for the YAML configuration file")
        console.print(json.dumps(cls.REQUIRES_CONFIG, indent=2))
    # show_info
# TranslatorService
