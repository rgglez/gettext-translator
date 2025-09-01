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

import logging
import sys
import polib
from translator_factory import TranslatorFactory
from settings import Settings
from pydantic import ValidationError
from rich.pretty import pprint

# -------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)

# -------------------------------------------------------------------------


class GettextCloudTranslator:
    def __init__(self, service) -> None:
        self.service = service
        self.config = service.config

        if not self.config.info and self.config.fuzzy:
            self.disable_fuzzy_translations()
    # __init__

    # -------------------------------------------------------------------------

    def disable_fuzzy_translations(self):
        """
        Disables fuzzy translations in a .po file by removing the 'fuzzy' flags from entries.
        """
        try:
            po_file = polib.pofile(self.config.po)

            fuzzy_entries = [entry for entry in po_file if 'fuzzy' in entry.flags]
            for entry in fuzzy_entries:
                entry.flags.remove('fuzzy')

            po_file.save(self.config.po)
            logging.info("Fuzzy translations disabled in file: %s", self.config.po)
        except Exception as e:  # pylint: disable=W0718
            logging.error("Error while disabling fuzzy translations in file %s: %s", self.config.po, e)
    # disable_fuzzy_translations

    # -------------------------------------------------------------------------

    def update_po_entry(self, original_text, translated_text, po_file):
        """Updates a .po file entry with the translated text."""
        entry = po_file.find(original_text)
        if entry:
            logging.info("Applying to %s", entry.msgid)
            entry.msgstr = translated_text
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
                logging.warning("No original text found for index %s", translation["msgid"])
    # apply_translations_to_po_file

    # -------------------------------------------------------------------------

    def process_translations(self, texts_to_translate):
        """Processes translations either in bulk or one by one."""
        if self.config.bulk:
            return self.service.translate_batch(texts_to_translate)
        else:
            return self.service.translate(texts_to_translate)
    # process_translations

    # -------------------------------------------------------------------------

    def translate(self):
        try:
            po_file = polib.pofile(self.config.po)
            file_lang = po_file.metadata.get('Language', '')

            if file_lang[:2] != self.config.dst.language:
                logging.warning("Skipping .po file due to inferred language mismatch: %s", self.config.po)
                return

            texts_to_translate = [
                entry.msgid
                for entry in po_file
                if not entry.msgstr and entry.msgid and 'fuzzy' not in entry.flags
            ]

            translated_texts = self.process_translations(texts_to_translate)

            logging.info("Applying %i translations to %s", len(translated_texts), self.config.po)
            self.apply_translations_to_po_file(translated_texts, po_file)

            po_file.save()

            logging.info("Finished processing .po file: %s", self.config.po)
        except Exception as e:  # pylint: disable=W0718
            logging.error("Error processing file %s: %s", self.config.po, e)
    # process_po_file

    # -------------------------------------------------------------------------

    def capabilities(self):
        pprint(self.service.get_capabilities().to_dict())
    # capabilities

    # -------------------------------------------------------------------------


# GettextCloudTranslator

# -----------------------------------------------------------------------------


if __name__ == "__main__":
    try:
        cli_args = Settings.parse_cli_args()
        settings = Settings(**{k: v for k, v in vars(cli_args).items() if v is not None})
    except ValidationError as e:
        print(e)
        sys.exit(1)

    if cli_args.info:
        translator = GettextCloudTranslator(TranslatorFactory().create_translator(settings))
        translator.capabilities()
        sys.exit(0)

    if cli_args.plugins:
        from gettext_translator_service import load_plugins
        plugins = load_plugins()
        pprint(plugins)
        sys.exit(0)

    translator = GettextCloudTranslator(TranslatorFactory().create_translator(settings))
    translator.translate()
# __main__
