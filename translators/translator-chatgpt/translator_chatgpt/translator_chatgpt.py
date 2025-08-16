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

import logging
from translator_service import TranslatorService
from openai import OpenAI

# -----------------------------------------------------------------------------


class TranslatorChatGPT(TranslatorService):
    def __init__(self, settings) -> None:
        self.config = settings
        self.client = OpenAI(api_key=self.config.apikey)

        # Validate the OpenAI connection
        if not self.validate_openai_connection():
            logging.error("OpenAI connection failed. Please check your API key and network connection.")
            exit()
    # __init__

    # -------------------------------------------------------------------------

    def validate_openai_connection(self):
        """Validates the OpenAI connection by making a test API call."""
        try:
            test_message = {"role": "system", "content": "Test message to validate connection."}
            self.client.chat.completions.create(model=self.config.model, messages=[test_message])
            logging.info("OpenAI connection validated successfully.")
            return True
        except Exception as e:  # pylint: disable=W0718
            logging.error("Failed to validate OpenAI connection: %s", e)
            return False
    # validate_openai_connection

    # -------------------------------------------------------------------------

    # def translate_bulk(self, texts, target_language, po_file_path, current_batch):
    """
    def translate_bulk(self, text) -> str:
        return
        # Translates a list of texts in bulk and handles retries.
        translated_texts = []
        for i, _ in enumerate(range(0, len(texts), self.config.batch_size), start=current_batch):
            batch_texts = texts[i:i + self.config.batch_size]
            batch_info = f"File: {po_file_path}, Batch {i}/{self.config.total_batches}"
            batch_info += f" (texts {i + 1}-{min(i + self.config.batch_size, len(texts))})"
            translation_request = (f"Translate the following texts from {self.config.source_language} "
                                "into {target_language}. "
                                "Use the format 'Index: Text' for each segment:\n\n")
            for index, text in enumerate(batch_texts, start=i * self.batch_size):
                translation_request += f"{index}: {text}\n"

            retries = 3

            while retries:
                try:
                    if self.config.bulk:
                        logging.info("Translating %s", batch_info)
                    self.perform_translation(translation_request, translated_texts, batch=True)
                    break
                except Exception as e:  # pylint: disable=W0718
                    error_message = f"Error in translating {batch_info}: {e}. Retrying... {retries - 1} attempts left."
                    logging.error(error_message)
                    if retries <= 1:
                        logging.error("Maximum retries reached for %s. Skipping this batch.", batch_info)
                        translated_texts.extend([''] * len(batch_texts))
                    retries -= 1
                    time.sleep(1)

        logging.debug("Translated texts: %s", translated_texts)
        return translated_texts
    """
    # translate_bulk

    # -------------------------------------------------------------------------

    def perform_translation(self, translation_request, translated_texts, batch=False):
        """Takes a translation request and appends the translated texts to the translated_texts list."""
        translated_texts = []

        message = {"role": "user", "content": translation_request}
        logging.debug("Translation request: %s", translation_request)
        completion = self.client.chat.completions.create(model=self.config.model, messages=[message])

        raw_response = completion.choices[0].message.content.strip()
        logging.info("Raw API response: %s", raw_response)

        if batch:
            for line in raw_response.split("\n"):
                try:
                    index_str, translation = line.split(": ", 1)
                    index = int(index_str.strip())
                    translation = translation.strip()
                    if translation and not translation.startswith("The provided text does not seem to be"):
                        translated_texts.append((index, translation))
                    else:
                        logging.error("No valid translation found for index %s", index)
                        translated_texts.append((index, ''))
                except ValueError:  # pylint: disable=W0718
                    logging.error("Error parsing line: '%s'", line)
                    translated_texts.append((index, ''))
        else:
            if not raw_response.startswith("The provided text does not seem to be"):
                translated_texts.append((0, raw_response))
            else:
                logging.error("No valid translation found for text")
                translated_texts.append((0, ''))
    # perform_translation

    # -------------------------------------------------------------------------

    def translate(self, texts_to_translate):
        """Translates texts one by one and updates the .po file."""
        translated_texts = []
        for index, text in enumerate(texts_to_translate):
            logging.info("Translating text %s/%s", (index + 1), len(texts_to_translate))
            translation_request = f"Translate the following text from \
                                    {self.config.src} into {self.config.dst}: {text}"
            result = self.service.perform_translation(translation_request)
            if result:
                translated_texts.append({
                    "msgid": text,
                    "msgstr": result[0][1]
                })
            else:
                logging.error("No translation returned for text: %s", text)
    # translate

    # -------------------------------------------------------------------------

    def translate_batch(self, texts):
        """Translates texts in bulk and applies them to the .po file."""
        self.total_batches = (len(texts) - 1) // 50 + 1
    #    translated_texts = self.service.translate_bulk(texts)
    # translate_batch
# TranslatorChatGPT
