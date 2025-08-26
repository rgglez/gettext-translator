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
import requests
import uuid

from gettext_translator_service import TranslatorService
from rich.pretty import pprint

# -----------------------------------------------------------------------------


class TranslatorAzure(TranslatorService):
    def __init__(self, settings) -> None:
        self.config = settings

        path = '/translate'
        self.constructed_url = 'https://api.cognitive.microsofttranslator.com' + path
        self.params = {
            'api-version': '3.0',
            'from': self.config.src,
            'to': self.config.dst,
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
        print("Bulk mode not supported by the Azure plugin")
        pass
    # translate_batch
# TranslatorAzure
