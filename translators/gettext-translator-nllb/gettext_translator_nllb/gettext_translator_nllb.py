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
import torch
import warnings
from rich.pretty import pprint
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

warnings.filterwarnings("ignore")

# -----------------------------------------------------------------------------

"""
Available models:
nllb-200-distilled-600M (faster, smaller)
nllb-200-1.3B (better quality)
nllb-200-3.3B (best quality, requires more memory)
"""


class TranslatorNLLB:
    # Configuration options required
    REQUIRES_CONFIG: list[str] = ["model"]

    # -------------------------------------------------------------------------

    def __init__(self, settings) -> None:
        self.config = settings
    # __init__

    # -------------------------------------------------------------------------

    def configure(self):
        # Load the model
        self.tokenizer = AutoTokenizer.from_pretrained("facebook/" + self.config.plugin_options["model"])
        self.model = AutoModelForSeq2SeqLM.from_pretrained("facebook/" + self.config.plugin_options["model"])

        # NLLB needs a 3-letter language code and the scripting system
        self.src_lang = self.config.src.to_alpha3() + "_" + self.config.src.script
        self.dst_lang = self.config.dst.to_alpha3() + "_" + self.config.dst.script

        # Use GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
    # configure

    # -------------------------------------------------------------------------

    def translate(self, texts_to_translate):
        try:
            self.configure()

            translated_texts = []

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

                # Generate translation. 512 is the maximun token length
                with torch.no_grad():
                    generated_tokens = self.model.generate(
                        **inputs,
                        forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(self.dst_lang),
                        max_length=512,
                        num_beams=5,
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
