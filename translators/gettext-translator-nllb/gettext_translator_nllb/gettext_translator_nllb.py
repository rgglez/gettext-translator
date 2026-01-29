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

import yaml
import torch
import warnings
import os
from rich.pretty import pprint
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from gettext_translator_service import TranslatorService

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

    def __init__(self, settings) -> None:
        self.config = settings
        
        if os.path.exists(self.config.config):
            with open(self.config.config) as stream:
                try:
                    yaml_file = yaml.safe_load(stream)
                    self.config.model = yaml_file["model"]
                except yaml.YAMLError as exc:
                    print(exc)
        else:
            raise Exception("[🚫] Configuration file not found")
    # __init__

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

    def translate(self, texts_to_translate):
        try:
            self.configure()

            translated_texts = []
            i = 0
            total = len(texts_to_translate)

            for text_entry in texts_to_translate:
                if 'id' not in text_entry:
                    print("[🚫] Input dictionary must contain 'id' field")
                    continue

                if "ctx" in text_entry:
                    # Combine context and text for better translation
                    input_text = f"Context: {text_entry["ctx"]} Text: {text_entry["id"]}"
                else:
                    input_text = text_entry["id"]
                # if

                # Tokenize with source language specification
                self.tokenizer.src_lang = self.src_lang
                inputs = self.tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
                inputs = inputs.to(self.device)

                i = i + 1
                print(f"[📝 {i}/{total}] {input_text}", i, total, input_text)

                # Generate translation. 512 is the maximun token length
                with torch.no_grad():
                    generated_tokens = self.model.generate(
                        **inputs,
                        forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(self.dst_lang),
                        max_length=50,
                        num_beams=1,
                        early_stopping=True
                    )
                # with

                # Decode the translation
                translation = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

                # Clean up the output if context was used
                if "ctx" in text_entry and text_entry["ctx"] and ":" in translation:
                    # Find the actual text after the last colon
                    # This handles translated "Text:" labels in any language
                    parts = translation.split(":")
                    if len(parts) > 1:
                        translation = parts[-1].strip()
                    # if
                # if

                result = {'msgid': text_entry["id"]}
                result['msgstr'] = translation
                if "ctx" in text_entry:
                    result['msgctxt'] = text_entry["ctx"]

                translated_texts.append(result)
            # for

            return translated_texts
        except Exception as e:  # pylint: disable=W0718
            pprint(e)
            traceback.print_stack()
            return []
    # translate
# TranslatorNLLB
