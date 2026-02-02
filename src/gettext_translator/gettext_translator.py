"""
Gettext Translator

This Python script provides a tool for translating gettext .po files
using OpenAI's API, Microsoft Azure Translator or local AI models.
It is designed to handle both bulk and individual translation modes.

---
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

# -------------------------------------------------------------------------

import logging
import sys
import polib
from translator_factory import TranslatorFactory
from settings import Settings
from logging_levels import LoggingLevels
from pydantic import ValidationError

# -------------------------------------------------------------------------


class GettextTranslator:
    def __init__(self, service) -> None:
        self.service = service
        self.config = service.config

        if self.config.fuzzy and not self.config.info:
            self.disable_fuzzy_translations()
    # __init__

    # -------------------------------------------------------------------------

    def disable_fuzzy_translations(self):
        """
        Disables fuzzy translations in a .po file by removing the 'fuzzy' flags from entries.
        """
        try:
            po_file = polib.pofile(self.config.po)

            # fuzzy_entries = [entry for entry in po_file if 'fuzzy' in entry.flags]
            # for entry in fuzzy_entries:
            #     entry.flags.remove('fuzzy')

            [entry.flags.discard('fuzzy') for entry in po_file if 'fuzzy' in entry.flags]

            po_file.save(self.config.po)

            logging.info("[✔️] Fuzzy translations disabled in file: %s", self.config.po)
        except Exception as e:  # pylint: disable=W0718
            logging.error("[💣] Error while disabling fuzzy translations in file %s: %s", self.config.po, e)
    # disable_fuzzy_translations

    # -------------------------------------------------------------------------

    def update_po_entry(self, original_text, translated_text, po_file):
        """Updates a .po file entry with the translated text."""
        entry = po_file.find(original_text)
        if entry:
            logging.info("[⚙️] Applying to %s", entry.msgid)
            entry.msgstr = translated_text
            if self.config.ascribe:
                entry.comment = "AI-translated"
    # update_po_entry

    # -------------------------------------------------------------------------

    def apply_translations_to_po_file(self, translated_texts, po_file):
        """
        Applies the translated texts to the .po file.
        """

        for translation in translated_texts:
            if translation["msgstr"]:
                self.update_po_entry(translation["msgid"], translation["msgstr"], po_file)
            else:
                logging.warning("[❌] No original text found for index %s", translation["msgid"])
    # apply_translations_to_po_file

    # -------------------------------------------------------------------------

    def translate(self):
        """
        Translates the PO file
        """
        try:
            po_file = polib.pofile(self.config.po)
            file_lang = po_file.metadata.get('Language', '')

            if file_lang[:2] != self.config.dst.language:
                logging.warning("[💣] Skipping .po file due to inferred language mismatch: %s", self.config.po)
                return

            texts_to_translate = [
                {"id": entry.msgid, "ctx": entry.msgctxt} if hasattr(entry, 'msgctxt') and entry.msgctxt else {"id": entry.msgid}
                for entry in po_file
                if not entry.msgstr and entry.msgid and 'fuzzy' not in entry.flags
            ]

            translated_texts = self.service.translate(texts_to_translate)

            logging.info("[⚙️] Applying %i translations to %s", len(translated_texts), self.config.po)

            self.apply_translations_to_po_file(translated_texts, po_file)

            po_file.save()

            logging.info("[✅] Finished processing .po file: %s", self.config.po)
        except Exception as e:  # pylint: disable=W0718
            logging.error("[☠️] Error processing file %s: %s", self.config.po, e)
    # process_po_file
# GettextTranslator

# -----------------------------------------------------------------------------


if __name__ == "__main__":
    try:
        cli_args = Settings.parse_cli_args()
        settings = Settings(**{k: v for k, v in vars(cli_args).items() if v is not None})
    except ValidationError as e:
        print(e)
        sys.exit(1)

    # Configure logging
    logging.basicConfig(level=LoggingLevels.get(settings.verbose))

    # Load the translation backend
    backend = TranslatorFactory().create_translator(settings)
    translator = GettextTranslator(backend)

    # Shows the info for the given --backend and exit
    if cli_args.info:
        backend.show_info()
        sys.exit(0)

    # Translate!
    translator.translate()
# __main__
