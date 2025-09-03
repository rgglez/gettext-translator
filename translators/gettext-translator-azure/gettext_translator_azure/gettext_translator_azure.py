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
import logging

from gettext_translator_service import TranslatorService
from rich.pretty import pprint

# -----------------------------------------------------------------------------


class TranslatorAzure(TranslatorService):
    # Configuration options required
    REQUIRES_CONFIG: list[str] = ["apikey", "location"]

    # -------------------------------------------------------------------------

    def __init__(self, settings) -> None:
        self.config = settings
    # __init__

    # -------------------------------------------------------------------------

    def configure(self):
        self.constructed_url = 'https://api.cognitive.microsofttranslator.com/translate'
        self.params = {
            'api-version': '3.0',
            'from': self.config.src.language,
            'to': self.config.dst.language,
            'textType': 'html'
        }
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.config.plugin_options["apikey"],
            # location required if you're using a multi-service or regional (not global) resource.
            'Ocp-Apim-Subscription-Region': self.config.plugin_options["location"],
            'Content-type': 'application/json',
            'X-ClientTraceId': str(uuid.uuid4())
        }
    # configure

    # -------------------------------------------------------------------------

    def translate(self, texts_to_translate):
        try:
            self.configure()

            translated_texts = []
            for text_entry in texts_to_translate:
                body = []
                body.append({
                    'text': text_entry["id"]
                })

                request = requests.post(self.constructed_url, params=self.params, headers=self.headers, json=body)
                if request.status_code == 200:
                    response = request.json()

                    translated_texts.append({
                        "msgid": text_entry["id"],
                        "msgctxt": text_entry["ctx"] if "ctx" in text_entry else "",
                        "msgstr": response[0]['translations'][0]['text']
                    })
                else:
                    logging.error("[🤐] Request to Azure service failed: %s", request.reason)
            # for

            return translated_texts

        except Exception as e:  # pylint: disable=W0718
            pprint(e)
            traceback.print_stack()
            return []
    # translate

    # -------------------------------------------------------------------------

    def get_required_configuration(self):
        meta = {}
        for name, typ in self.__annotations__.items():
            value = getattr(self, name, None)
            meta[name] = value

        return meta
    # get_required_configuration
# TranslatorAzure
