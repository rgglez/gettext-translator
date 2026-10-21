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

from gettext_translator_service import TranslatorService, translate_plain
from transformers import MarianMTModel, MarianTokenizer

# -----------------------------------------------------------------------------


class TranslatorMarianMT(TranslatorService):
    # Configuration options required
    REQUIRES_CONFIG: list[str] = []

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

    def translate_strings(self, strings):
        batch_size = 100

        translated = []
        for i in range(0, len(strings), batch_size):
            batch = strings[i:i + batch_size]

            # Tokenize the batch (padding + truncation for uniformity, 512 is the model limit)
            inputs = self.tokenizer(
                [string["id"] for string in batch],
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            )

            # Generate and decode the translations
            outputs = self.model.generate(**inputs)
            translated += self.tokenizer.batch_decode(outputs, skip_special_tokens=True)
        # for

        return translated
    # translate_strings

    # -------------------------------------------------------------------------

    def translate(self, items):
        return translate_plain(items, self.translate_strings)
    # translate
# TranslatorMarianMT
