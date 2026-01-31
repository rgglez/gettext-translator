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

import traceback

from gettext_translator_service import TranslatorService
from transformers import MarianMTModel, MarianTokenizer
from rich.pretty import pprint

# -----------------------------------------------------------------------------


class TranslatorMarianMT(TranslatorService):
    # Configuration options required
    REQUIRES_CONFIG: list[str] = []

    # -------------------------------------------------------------------------

    def __init__(self, settings) -> None:
        self.config = settings
    # __init__

    # -------------------------------------------------------------------------

    def configure(self):
        # Include the territory if present
        source_lang = self.config.src.language
        target_lang = self.config.dst.language

        self.model_name = f"Helsinki-NLP/opus-mt-{source_lang}-{target_lang}"
        self.tokenizer = MarianTokenizer.from_pretrained(self.model_name)
        self.model = MarianMTModel.from_pretrained(self.model_name)
    # configure

    # -------------------------------------------------------------------------

    def translate(self, texts_to_translate):
        try:
            self.configure()

            batch_size = 100

            translated_texts = []

            for i in range(0, len(texts_to_translate), batch_size):
                batch = texts_to_translate[i:i + batch_size]

                # Extract texts for translation
                texts_for_translation = [entry["id"] for entry in batch]

                # Tokenize the batch (padding + truncation for uniformity)
                inputs = self.tokenizer(
                    texts_for_translation,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=1024  # Adjust based on your needs
                )

                # Generate translations
                outputs = self.model.generate(**inputs)

                # Decode the batch
                translated_batch = self.tokenizer.batch_decode(
                    outputs,
                    skip_special_tokens=True
                )

                # Create dictionary entries with msgid, msgstr, and optional msgctxt
                for entry, translated in zip(batch, translated_batch):
                    result = {
                        "msgid": entry["id"],
                        "msgstr": translated
                    }

                    # Add msgctxt if context exists
                    if "ctx" in entry or len(self.config.context) > 0:
                        result["msgctxt"] = entry["ctx"] if "ctx" in entry else self.config.context

                    translated_texts.append(result)
                # for
            # for

            return translated_texts

        except Exception as e:  # pylint: disable=W0718
            pprint(e)
            traceback.print_stack()
            return []
    # translate
# TranslatorMarianMT
