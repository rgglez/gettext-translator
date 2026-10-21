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

import logging
import warnings

import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from gettext_translator_service import TranslatorService, translate_plain

warnings.filterwarnings("ignore")

# -----------------------------------------------------------------------------

"""
Available models:
nllb-200-distilled-600M (faster, smaller)
nllb-200-1.3B (better quality)
nllb-200-3.3B (best quality, requires more memory)
"""


class TranslatorNLLB(TranslatorService):
    # Configuration options required
    REQUIRES_CONFIG: list[str] = ["model"]

    # -------------------------------------------------------------------------

    def configure(self):
        # Use GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Load the model
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/" + self.config.model)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            "facebook/" + self.config.model,
            tie_word_embeddings=False,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto"
        )

        # NLLB needs a 3-letter language code and the scripting system
        self.src_lang = self.config.src.to_alpha3() + "_" + self.config.src.script
        self.dst_lang = self.config.dst.to_alpha3() + "_" + self.config.dst.script

        self.model.to(self.device)
    # configure

    # -------------------------------------------------------------------------

    def translate_strings(self, strings):
        translated = []
        total = len(strings)

        for i, string in enumerate(strings, 1):
            if "ctx" in string:
                # Combine context and text for better translation
                input_text = f"Context: {string['ctx']} Text: {string['id']}"
            else:
                input_text = string["id"]
            # if

            # Tokenize with source language specification
            self.tokenizer.src_lang = self.src_lang
            inputs = self.tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
            inputs = inputs.to(self.device)

            logging.info("[📝 %d/%d] %s", i, total, input_text)

            # Generate translation. 512 is the maximum token length of the model
            with torch.no_grad():
                generated_tokens = self.model.generate(
                    **inputs,
                    forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(self.dst_lang),
                    max_length=512,
                    num_beams=1,
                    early_stopping=True
                )
            # with

            # Decode the translation
            translation = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

            # Clean up the output if context was used
            if "ctx" in string and ":" in translation:
                # Find the actual text after the last colon
                # This handles translated "Text:" labels in any language
                translation = translation.split(":")[-1].strip()
            # if

            translated.append(translation)
        # for

        return translated
    # translate_strings

    # -------------------------------------------------------------------------

    def translate(self, items):
        return translate_plain(items, self.translate_strings)
    # translate
# TranslatorNLLB
