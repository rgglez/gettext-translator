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


from google import genai
from google.genai import types
from gettext_translator_service import TranslatorService, translate_llm

# -----------------------------------------------------------------------------


class TranslatorGemini(TranslatorService):
    # Configuration options required
    REQUIRES_CONFIG: list[str] = ["apikey", "model"]

    # -------------------------------------------------------------------------

    def configure(self):
        # Configure the API key
        self.client = genai.Client(api_key=self.config.apikey)
    # configure

    # -------------------------------------------------------------------------

    def call(self, system_prompt, user_message):
        response = self.client.models.generate_content(
            model=self.config.model,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=getattr(self.config, "temperature", 0.3),
                response_mime_type="application/json",
            ),
        )
        return response.text
    # call

    # -------------------------------------------------------------------------

    def translate(self, items):
        return translate_llm(items, self.config, self.call)
    # translate
# TranslatorGemini
