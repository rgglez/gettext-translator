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

import os
import yaml
import traceback
import requests
import uuid
import logging

from gettext_translator_service import TranslatorService
from rich.pretty import pprint

# -----------------------------------------------------------------------------


class TranslatorAzure(TranslatorService):
    # Configuration options required
    REQUIRES_CONFIG: list[str] = ["apikey", "location", "endpoint"]

    # -------------------------------------------------------------------------

    def __init__(self, settings) -> None:
        self.config = settings

        if not self.config.info:
            if os.path.exists(self.config.config):
                with open(self.config.config) as stream:
                    try:
                        yaml_file = yaml.safe_load(stream)
                        self.config.location = yaml_file["location"]
                        self.config.endpoint = yaml_file["endpoint"]
                        if "env:" in yaml_file["apikey"]:
                            self.config.apikey = os.getenv(yaml_file["apikey"].replace("env:", ""))
                        else:
                            self.config.apikey = yaml_file["apikey"]

                    except yaml.YAMLError as exc:
                        print(exc)
    # __init__

    # -------------------------------------------------------------------------

    def configure(self):
        self.constructed_url = self.config.endpoint + '/translate'
        self.params = {
            'api-version': '3.0',
            'from': self.config.src.language,
            'to': self.config.dst.language,
            'textType': 'html'
        }
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.config.apikey,
            # location required if using a multi-service or regional (not global) resource.
            'Ocp-Apim-Subscription-Region': self.config.location,
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
# TranslatorAzure
