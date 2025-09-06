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
        source_lang = self.config.src.language + (("_" + self.config.src.territory) if self.config.src.territory else "")
        target_lang = self.config.dst.language + (("_" + self.config.src.territory) if self.config.src.territory else "")

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
                    if "ctx" in entry and entry["ctx"]:
                        result["msgctxt"] = entry["ctx"]

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
