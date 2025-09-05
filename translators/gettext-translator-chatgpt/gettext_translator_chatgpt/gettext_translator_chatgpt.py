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


import json
import logging
from gettext_translator_service import TranslatorService
from openai import OpenAI

# -----------------------------------------------------------------------------


class TranslatorChatGPT(TranslatorService):
    # Configuration options required
    REQUIRES: list[str] = ["apikey", "model"]

    # -------------------------------------------------------------------------

    def __init__(self, settings) -> None:
        self.config = settings
    # __init__

    # -------------------------------------------------------------------------

    def configure(self):
        self.client = OpenAI(api_key=self.config.plugin_options["apikey"])

        # Validate the OpenAI connection
        if not self.validate_openai_connection():
            logging.error("[☠️] OpenAI connection failed. Please check your API key and network connection.")
            exit()
    # configure

    # -------------------------------------------------------------------------

    def validate_openai_connection(self):
        """Validates the OpenAI connection by making a test API call."""
        try:
            test_message = {"role": "system", "content": "Test message."}
            self.client.chat.completions.create(model=self.config.plugin_options["model"], messages=[test_message])
            logging.info("[✔️] OpenAI connection validated successfully.")
            return True
        except Exception as e:  # pylint: disable=W0718
            logging.error("[☠️] Failed to validate OpenAI connection: %s", e)
            return False
    # validate_openai_connection

    # -------------------------------------------------------------------------

    def perform_translation(self, translation_request):
        """Takes a translation request and appends the translated texts to the translated_texts list."""
        message = {"role": "user", "content": translation_request}
        logging.debug("[ℹ️] Translation request: %s", translation_request)
        completion = self.client.chat.completions.create(model=self.config.plugin_options["model"], messages=[message])

        response = completion.choices[0].message.content.strip()

        logging.info("[ℹ️] Raw API response: %s", response)

        try:
            result = json.loads(response)
        except Exception as e:
            logging.error("[☠️] Failed to translate batch: %s", e)
            return []

        return result
    # perform_translation

    # -------------------------------------------------------------------------

    def translate(self, texts_to_translate):
        self.configure()

        batch_size = 100
        translated_texts = []

        source_language = self.config.src.display_name("en")
        destination_language = self.config.dst.display_name("en")

        translation_prompt = """
Translate the following strings from {} to {}. The strings are given
in the form of a JSON array:

[{{"id":"Original string","ctx":"The context of the string"}}]

where "ctx" is optional and denotes the context in which the string is used.

Answer with an array of JSON in this form:

[{{"msgid":"Original string", "msgstr":"Translated string", "msgctxt":"The context of the string"}}]

Answer just with the translation results, do not add any other text. If an error occurs
or a translation does not exist for a given "id", use an empty string for "msgstr".

The texts to translate follow:


""".format(source_language, destination_language)

        # Form the rest of the prompt:
        for i in range(0, len(texts_to_translate), batch_size):
            body = []

            # Process current batch
            batch = texts_to_translate[i:i + batch_size]

            for text_entry in batch:
                if "ctx" in text_entry:
                    body.append({
                        'id': text_entry["id"],
                        'ctx': text_entry["ctx"]
                    })
                else:
                    body.append({
                        'id': text_entry["id"]
                    })
            # for

            # Translate batch
            json_to_translate = json.dumps(body)
            results = self.perform_translation(translation_prompt + json_to_translate)
            for entry in results:
                translated_texts.append(entry)
        # for

        return translated_texts
    # translate
# TranslatorChatGPT
