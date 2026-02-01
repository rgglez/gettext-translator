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


import json
import logging
import os

import yaml
from gettext_translator_service import TranslatorService
from openai import OpenAI

# -----------------------------------------------------------------------------


class TranslatorChatGPT(TranslatorService):
    # Configuration options required
    REQUIRES: list[str] = ["apikey", "model"]

    # -------------------------------------------------------------------------

    def __init__(self, settings) -> None:
        self.config = settings

        if not self.config.info:
            if os.path.exists(self.config.config):
                with open(self.config.config) as stream:
                    try:
                        yaml_file = yaml.safe_load(stream)
                        self.config.model = yaml_file["model"]
                        if "env:" in yaml_file["apikey"]:
                            self.config.apikey = os.getenv(yaml_file["apikey"].replace("env:", ""))
                        else:
                            self.config.apikey = yaml_file["apikey"]

                    except yaml.YAMLError as exc:
                        raise exc
            else:
                raise Exception("[🚫] Configuration file not found")
    # __init__

    # -------------------------------------------------------------------------

    def configure(self):
        self.client = OpenAI(api_key=self.config.apikey)

        # Validate the OpenAI connection
        if not self.validate_openai_connection():
            logging.error("[☠️] OpenAI connection failed. Please check your API key and network connection.")
            exit()
    # configure

    # -------------------------------------------------------------------------

    def validate_openai_connection(self):
        """Validates the OpenAI connection by making a test API call."""
        try:
            self.client.models.list()
            logging.info("[✔️] Valid connection to OpenAI API (using list_models).")
            return True
        except Exception as e:
            logging.error("[☠️] Connection error to OpenAI API: %s", e)
            return False
    # validate_openai_connection

    # -------------------------------------------------------------------------

    def perform_translation(self, translation_request):
        """Takes a translation request and appends the translated texts to the translated_texts list."""
        try:
            message = {"role": "user", "content": translation_request}

            logging.debug("[ℹ️] Translation request: %s", translation_request)

            completion = self.client.chat.completions.create(model=self.config.model, messages=[message])
            response = completion.choices[0].message.content.strip()

            logging.debug("[ℹ️] Raw API response: %s", response)

            result = json.loads(response)
        except Exception as e:
            logging.error("[☠️] Failed to translate: %s", e)
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
You are an expert translator. Translate the following strings
from {} to {}. The strings are given in the form of a JSON array:

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
                if "ctx" in text_entry or len(self.config.context) > 0:
                    body.append({
                        'id': text_entry["id"],
                        'ctx': text_entry["ctx"] if "ctx" in text_entry else self.config.context
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
