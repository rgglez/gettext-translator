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
import uuid

import requests
from gettext_translator_service import TranslatorService, translate_plain

# -----------------------------------------------------------------------------

# The API accepts up to 1000 texts per request
BATCH_SIZE = 100

# -----------------------------------------------------------------------------


class TranslatorAzure(TranslatorService):
    # Configuration options required
    REQUIRES_CONFIG: list[str] = ["apikey", "location", "endpoint"]

    # -------------------------------------------------------------------------

    def configure(self):
        self.constructed_url = self.config.endpoint.rstrip('/') + '/translate'
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

    def translate_strings(self, strings):
        translated = []
        for i in range(0, len(strings), BATCH_SIZE):
            batch = strings[i:i + BATCH_SIZE]
            body = [{'text': string["id"]} for string in batch]

            try:
                request = requests.post(self.constructed_url, params=self.params, headers=self.headers, json=body,
                                        timeout=60)
                request.raise_for_status()
                translated += [response['translations'][0]['text'] for response in request.json()]
            except Exception as e:  # pylint: disable=W0718
                logging.warning("[🤐] Request to Azure service failed for %d strings: %s", len(batch), e)
                translated += [None] * len(batch)
        # for

        return translated
    # translate_strings

    # -------------------------------------------------------------------------

    def translate(self, items):
        return translate_plain(items, self.translate_strings)
    # translate
# TranslatorAzure
