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


from gettext_translator_service import TranslatorService, translate_llm
from openai import OpenAI

# -----------------------------------------------------------------------------


class TranslatorChatGPT(TranslatorService):
    # Configuration options required
    REQUIRES_CONFIG: list[str] = ["apikey", "model"]

    # -------------------------------------------------------------------------

    def configure(self):
        self.client = OpenAI(api_key=self.config.apikey)

        # Validate the OpenAI connection
        try:
            self.client.models.list()
        except Exception as e:
            raise RuntimeError(f"OpenAI connection failed, check your API key and network connection: {e}") from e
    # configure

    # -------------------------------------------------------------------------

    def call(self, system_prompt, user_message):
        completion = self.client.chat.completions.create(
            model=self.config.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
        )
        return completion.choices[0].message.content
    # call

    # -------------------------------------------------------------------------

    def translate(self, items):
        return translate_llm(items, self.config, self.call)
    # translate
# TranslatorChatGPT
