"""
Gettext Translator

This Python script provides a tool for translating gettext .po files
using cloud services (OpenAI, Gemini, Azure Translator) or local AI models.

---
    AI-based Gettext automatic translator.
    Copyright (C) 2026 Rodolfo González González.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# -------------------------------------------------------------------------

import logging
import re
import sys
from collections import Counter
from pathlib import Path

import polib
from langcodes import Language, LanguageTagError
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .settings import Settings
from .translator_factory import TranslatorFactory

# -------------------------------------------------------------------------

AI_COMMENT = "AI-translated"

# The gettext format flags whose placeholders are checked; any other entry gets every check below
PRINTF_FLAGS = {"c-format", "objc-format", "python-format", "php-format"}
NO_PRINTF_FLAGS = {"no-" + flag for flag in PRINTF_FLAGS}
BRACE_FLAGS = {"python-brace-format"}
QT_FLAGS = {"qt-format", "qt-plural-format", "kde-format"}

# printf-style (%s, %1$s, %(name)s, %.2f, %ld); %% is matched only to be skipped. Groups: position, name, conversion
PRINTF = (r"%%|%(?:(\d+)\$|\(([^)]*)\))?[-+#0{flags}]*(?:\d+|\*)?(?:\.(?:\d+|\*))?"
          r"(?:hh|h|ll|l|L|q|j|z|t)?([diouxXeEfFgGaAcspr])")
PRINTF_RE = re.compile(PRINTF.format(flags=" '"))
# Without a format flag the space and ' flags are left out, so "100% done" is not read as "% d"
LOOSE_PRINTF_RE = re.compile(PRINTF.format(flags=""))
# Brace-style ({name}, {0}, {}); {{ and }} are literals
BRACE_RE = re.compile(r"\{\{|\}\}|(\{[^{}]*\})")
# Qt/KDE (%1, %L1); in "%1%" the second % is a literal
QT_RE = re.compile(r"%%|(%L?\d+)")
TAG_RE = re.compile(r"</?([a-zA-Z][\w-]*)")
# ponytail: fixed list of HTML/Pango inline tags, so <number> or <invalid> are text, not markup.
# KUIT tags (<command>, <placeholder>) clash with command-line metavariables; add them for kde-format if needed
HTML_TAGS = frozenset("a b i u s em strong span br p code tt big small sub sup kbd pre ul ol li div img font hr "
                      "h1 h2 h3 h4 h5 h6 table tr td th markup".split())

# -------------------------------------------------------------------------


def printf_args(text, regex):
    """Returns the printf directives as "argument$conversion", so "%s %d" and "%2$d %1$s" give the same ones."""
    args, n = [], 0
    for position, name, conversion in regex.findall(text):
        if conversion:  # not %%
            if not position and not name:
                n += 1
            args.append(f"{position or name or n}${conversion}")
    return args
# printf_args

# -------------------------------------------------------------------------


def placeholders(text: str, flags=()) -> Counter:
    """Returns the placeholders and tags of text, read with the syntax given by the entry's format flags."""
    flags = set(flags)
    found = [m.group(0) for m in TAG_RE.finditer(text) if m.group(1).lower() in HTML_TAGS]

    if flags & (PRINTF_FLAGS | BRACE_FLAGS | QT_FLAGS):
        if flags & PRINTF_FLAGS:
            found += printf_args(text, PRINTF_RE)
        if flags & BRACE_FLAGS:
            found += [m for m in BRACE_RE.findall(text) if m]
        if flags & QT_FLAGS:
            found += [m for m in QT_RE.findall(text) if m]
    else:
        if not flags & NO_PRINTF_FLAGS:
            found += printf_args(text, LOOSE_PRINTF_RE)
        rest = LOOSE_PRINTF_RE.sub("", text)
        found += [m for m in BRACE_RE.findall(rest) + QT_RE.findall(rest) if m]

    return Counter(found)
# placeholders

# -------------------------------------------------------------------------


def nplurals(po_file) -> int:
    match = re.search(r"nplurals\s*=\s*(\d+)", po_file.metadata.get("Plural-Forms", ""))
    return int(match.group(1)) if match else 2
# nplurals

# -------------------------------------------------------------------------


def validate(key, result, flags=()):
    """Returns the translation in result if it can be used for key, None otherwise. flags are the entry's flags."""
    _, msgid, plural, n = key

    def found(text):
        return placeholders(text, flags)

    if plural:
        forms = result.get("msgstr_plural")
        if not (isinstance(forms, list) and len(forms) == n and all(isinstance(f, str) and f for f in forms)):
            return None
        # Some forms may drop placeholders ("One file"), but the last and most general one must keep them
        allowed = found(msgid) | found(plural)
        if all(found(f) <= allowed for f in forms) and found(forms[-1]) == found(plural):
            return forms
        return None

    msgstr = result.get("msgstr")
    if isinstance(msgstr, str) and msgstr and found(msgstr) == found(msgid):
        return msgstr
    return None
# validate

# -------------------------------------------------------------------------


class GettextTranslator:
    def __init__(self, service, cache=None) -> None:
        self.service = service
        self.config = service.config
        self.cache = cache
    # __init__

    # -------------------------------------------------------------------------

    def po_files(self):
        """Returns (file, root) pairs. root is the directory the --output path is relative to."""
        files = []
        for path in map(Path, self.config.po):
            if path.is_dir():
                files += [(f, path) for f in sorted(path.rglob("*.po"))]
            else:
                files.append((path, path.parent))
        return files
    # po_files

    # -------------------------------------------------------------------------

    def output_path(self, path, root):
        if not self.config.output:
            return path
        output = Path(self.config.output)
        return output if output.suffix == ".po" else output / path.relative_to(root)
    # output_path

    # -------------------------------------------------------------------------

    def load(self, path):
        """Loads a .po file, or returns None if its language is not the destination language."""
        po_file = polib.pofile(str(path))
        file_lang = po_file.metadata.get("Language", "")

        try:
            language = Language.get(file_lang).language
        except LanguageTagError:
            language = None

        if language != self.config.dst.language:
            logging.warning("[💣] Skipping %s: its language %r is not %s", path, file_lang, self.config.dst.language)
            return None

        if self.config.fuzzy:
            for entry in po_file:
                entry.fuzzy = False
            logging.info("[✔️] Fuzzy translations disabled in file: %s", path)

        return po_file
    # load

    # -------------------------------------------------------------------------

    @staticmethod
    def item(n, key):
        ctx, msgid, plural, count = key
        item = {"n": n, "id": msgid}
        if ctx:
            item["ctx"] = ctx
        if plural:
            item["plural"] = plural
            item["nplurals"] = count
        return item
    # item

    # -------------------------------------------------------------------------

    def apply(self, entry, value):
        if isinstance(value, list):
            entry.msgstr_plural = dict(enumerate(value))
        else:
            entry.msgstr = value

        if self.config.ascribe and AI_COMMENT not in entry.comment:
            entry.comment = f"{entry.comment}\n{AI_COMMENT}".strip()
    # apply

    # -------------------------------------------------------------------------

    def request(self, pending, flags):
        """Sends the pending keys to the backend and returns the valid translations. flags maps keys to entry flags."""
        self.service.configure()
        results = self.service.translate([self.item(n, key) for n, key in enumerate(pending)])

        translations = {}
        for result in results:
            n = result.get("n")
            if not isinstance(n, int) or not 0 <= n < len(pending):
                logging.warning("[❌] Discarding result with unknown item number: %r", result)
                continue
            value = validate(pending[n], result, flags.get(pending[n], ()))
            if value is None:
                logging.warning("[❌] Discarding invalid translation for %r: %r", pending[n][1], result)
                continue
            translations[pending[n]] = value
        # for

        return translations
    # request

    # -------------------------------------------------------------------------

    def show(self, translations):
        table = Table("msgctxt", "msgid", "msgstr", show_lines=True)
        for (ctx, msgid, plural, _), value in translations.items():
            source = f"{msgid}\n{plural}" if plural else msgid
            target = "\n".join(value) if isinstance(value, list) else value
            table.add_row(Text(ctx), Text(source), Text(target))
        Console().print(table)
    # show

    # -------------------------------------------------------------------------

    def translate(self) -> bool:
        """
        Translates the .po files. Returns False if there was something to translate but nothing was translated.
        """
        files = self.po_files()
        if self.config.output.endswith(".po") and len(files) != 1:
            raise ValueError("--output can be a .po file only when translating a single .po file")

        # Group the untranslated entries of all the files by what has to be translated,
        # so each unique string is translated only once
        groups = {}
        flags = {}  # key -> format flags of its entries, used to validate the translation
        loaded = []
        for path, root in files:
            po_file = self.load(path)
            if po_file is None:
                continue

            count = nplurals(po_file)
            for entry in po_file.untranslated_entries():
                key = (entry.msgctxt or self.config.context, entry.msgid, entry.msgid_plural,
                       count if entry.msgid_plural else 0)
                groups.setdefault(key, []).append(entry)
                flags.setdefault(key, set()).update(entry.flags)
            loaded.append((path, root, po_file))
        # for

        translations = {}
        if self.cache:
            for key in groups:
                value = self.cache.get(key)
                if value is not None:
                    translations[key] = value
        cached = len(translations)

        pending = [key for key in groups if key not in translations]
        logging.info("[⚙️] %d strings to translate, %d from cache", len(pending), cached)

        new = self.request(pending, flags) if pending else {}
        if self.cache:
            for key, value in new.items():
                self.cache.put(key, value)
        translations.update(new)

        for key, entries in groups.items():
            if key in translations:
                for entry in entries:
                    self.apply(entry, translations[key])

        missing = len(pending) - len(new)
        if missing:
            logging.warning("[❌] %d of %d strings were not translated", missing, len(pending))

        if self.config.dry_run:
            self.show(translations)
            print(f"{len(new)} translated, {cached} from cache, {missing} not translated. No file was saved.")
        else:
            for path, root, po_file in loaded:
                output = self.output_path(path, root)
                output.parent.mkdir(parents=True, exist_ok=True)
                po_file.save(str(output))
                logging.info("[✅] Saved %s", output)

        return not pending or bool(new)
    # translate
# GettextTranslator

# -----------------------------------------------------------------------------


def main(argv=None) -> int:
    try:
        settings = Settings(**vars(Settings.parse_cli_args(argv)))
    except ValidationError as e:
        print(e)
        return 1

    logging.basicConfig(level=settings.verbose.upper())

    try:
        backend = TranslatorFactory().create_translator(settings)

        # Shows the info for the given --backend and exit
        if settings.info:
            backend.show_info()
            return 0

        cache = None
        if settings.cache:
            # Imported here because some Python builds lack sqlite3, which is only needed for --cache
            from .cache import TranslationCache
            scope = (settings.backend, str(getattr(settings, "model", "")), str(settings.src), str(settings.dst))
            cache = TranslationCache(settings.cache, scope)

        ok = GettextTranslator(backend, cache).translate()
    except Exception as e:  # pylint: disable=W0718
        logging.error("[☠️] %s", e, exc_info=settings.verbose == "debug")
        return 1

    return 0 if ok else 1
# main


if __name__ == "__main__":
    sys.exit(main())
