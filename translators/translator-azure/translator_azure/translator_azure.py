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

import traceback
import requests
import uuid

from translator_service import TranslatorService
from rich.pretty import pprint

# -----------------------------------------------------------------------------


class TranslatorAzure(TranslatorService):
    def __init__(self, settings) -> None:
        self.config = settings

        path = '/translate'
        self.constructed_url = 'https://api.cognitive.microsofttranslator.com' + path
        self.params = {
            'api-version': '3.0',
            'from': self.config.srclang,
            'to': self.config.dstlang,
            'textType': 'html'
        }
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.config.apikey,
            # location required if you're using a multi-service or regional (not global) resource.
            'Ocp-Apim-Subscription-Region': self.config.location,
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
    # __init__

    # -------------------------------------------------------------------------

    def translate(self, texts_to_translate):
        try:
            translated_texts = []
            for msgid in texts_to_translate:
                body = []
                body.append({
                    'text': msgid
                })

                request = requests.post(self.constructed_url, params=self.params, headers=self.headers, json=body)
                response = request.json()

                translated_texts.append({
                    "msgid": msgid,
                    "msgstr": response[0]['translations'][0]['text']
                })
            # for

            return translated_texts

        except Exception as e:  # pylint: disable=W0718
            pprint(e)
            traceback.print_stack()
            return []
    # translate

    # -------------------------------------------------------------------------

    def translate_batch(self, texts_to_translate):
        try:
            char_count = 0
            total_texts = len(texts_to_translate)
            translated_texts = []
            body = []
            i = 0
            j = 0

            for msgid in texts_to_translate:
                i = i + 1
                j = j + 1
                body.append({
                    'text': msgid
                })
                char_count = char_count + len(msgid)
                if char_count > 49500 or i + 1 > total_texts or j + 1 > 1000:
                    request = requests.post(self.constructed_url, params=self.params, headers=self.headers, json=body)
                    response = request.json()

                    for translation, original in zip(response, body):
                        translated_texts.append({
                            "msgid": original['text'],
                            "msgstr": translation['translations'][0]['text']
                        })
                    # for

                    body = []
                    char_count = 0
                    j = 0
                # if
            # for

            return translated_texts

        except Exception as e:  # pylint: disable=W0718
            pprint(e)
            traceback.print_stack()
            return []
    # translate_batch
# TranslatorAzure
