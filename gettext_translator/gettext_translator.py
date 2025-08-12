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

import argparse
import logging
import sys
import polib
from pydantic import ValidationError
from version import __version__
from translator_factory import TranslatorFactory
from settings import Settings, YamlConfigSettingsSource

# -------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)

# -------------------------------------------------------------------------


class GettextCloudTranslator:
    def __init__(self, service) -> None:
        self.service = service
        self.config = service.config

        if self.config.fuzzy:
            self.disable_fuzzy_translations(self.config.file)        
    # __init__

    # -------------------------------------------------------------------------

    def disable_fuzzy_translations(self):
        """
        Disables fuzzy translations in a .po file by removing the 'fuzzy' flags from entries.
        """
        try:
            po_file = polib.pofile(self.config.file)

            fuzzy_entries = [entry for entry in po_file if 'fuzzy' in entry.flags]
            for entry in fuzzy_entries:
                entry.flags.remove('fuzzy')

            self.po_file.save(self.config.file)
            logging.info("Fuzzy translations disabled in file: %s", self.config.file)
        except Exception as e:  # pylint: disable=W0718
            logging.error("Error while disabling fuzzy translations in file %s: %s", self.config.filepo_file_path, e)    
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
            return self.service.translate_in_bulk(texts_to_translate)
        else:
            return self.service.translate_one_by_one(texts_to_translate)
    # process_translations

    # -------------------------------------------------------------------------

    def translate(self):
        try:
            po_file = polib.pofile(self.config.file)
            file_lang = po_file.metadata.get('Language', '')
            
            if file_lang[:2] != self.config.dstlang:
                logging.warning("Skipping .po file due to inferred language mismatch: %s", self.config.file)
                return

            texts_to_translate = [
                entry.msgid
                for entry in po_file
                if not entry.msgstr and entry.msgid and 'fuzzy' not in entry.flags
            ]
            
            translated_texts = self.process_translations(texts_to_translate)

            logging.info("Applying %i translations to %s", len(translated_texts), self.config.file)
            self.apply_translations_to_po_file(translated_texts, po_file)

            po_file.save()

            logging.info("Finished processing .po file: %s", self.config.file)
        except Exception as e:  # pylint: disable=W0718
            logging.error("Error processing file %s: %s", self.config.file, e)    
    # process_po_file
# GettextCloudTranslator

# -----------------------------------------------------------------------------


def parse_cli_args():
    parser = argparse.ArgumentParser(description="Translate .po files")
    parser.add_argument("--version", action="version", version=f'%(prog)s {__version__}')
    parser.add_argument("--backend", type=str, required=True, default="azure", choices=["chatgpt", "azure"])
    parser.add_argument("--apikey", type=str, help="Service API key")
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo-1106", help="OpenAI model to use for translations, "
                        "for the ChatGPT backend.")
    parser.add_argument("--location", type=str, help="Microsoft Azure location")
    parser.add_argument("--po", type=str, required=True, help="Input .po file")
    parser.add_argument("--src", type=str, required=False, choices=["en", "es"], default="en", help="The ISO code for "
                        "the language of the source strings. Defaults to 'en' (English)")
    parser.add_argument("--dst", type=str, required=False, help="The ISO code for the language to translate to")
    parser.add_argument("--fuzzy", type=lambda x: x.lower() in ["true", "1", "yes"], help="Remove fuzzy entries")
    parser.add_argument("--bulk", type=lambda x: x.lower() in ["true", "1", "yes"], help="Use bulk translation mode")
    parser.add_argument("--bulksize", type=int, help="Batch size for bulk translation")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to the configuration file")
    args = parser.parse_args()
    return args

# -----------------------------------------------------------------------------


if __name__ == "__main__":
    cli_args = parse_cli_args()

    class MySettings(Settings):
        @classmethod
        def settings_customise_sources(cls, settings_cls, init_settings, env_settings):
            return (
                YamlConfigSettingsSource(settings_cls, cli_args.config),
                env_settings,
                init_settings,
            )

    try:
        settings = MySettings(**{k: v for k, v in vars(cli_args).items() if v is not None})
        print(settings.model_dump())
    except ValidationError as e:
        print(e)
        sys.exit(1)

    translator = GettextCloudTranslator(TranslatorFactory().create_translator(settings))
    translator.translate()
# __main__
