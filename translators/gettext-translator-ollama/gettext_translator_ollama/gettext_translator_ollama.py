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


from ollama import Client
from gettext_translator_service import TranslatorService, translate_llm

# -----------------------------------------------------------------------------


class TranslatorOllama(TranslatorService):
    # Configuration options required
    REQUIRES_CONFIG: list[str] = ["ollama", "model"]

    # -------------------------------------------------------------------------

    def configure(self):
        self.client = Client(host=self.config.ollama)

        # Validate the Ollama connection and that the model exists
        try:
            self.client.show(self.config.model)
        except Exception as e:
            raise RuntimeError(f"Ollama connection failed: {e}") from e
    # configure

    # -------------------------------------------------------------------------

    def call(self, system_prompt, user_message):
        response = self.client.generate(
            model=self.config.model,
            system=system_prompt,
            prompt=user_message,
            format="json",
            # Thinking models (qwen3...) in JSON mode return the answer in "thinking" and an empty "response"
            think=False,
            options={
                "temperature": getattr(self.config, "temperature", 0.1),
            }
        )
        return response.response or response.thinking or ""
    # call

    # -------------------------------------------------------------------------

    def translate(self, items):
        return translate_llm(items, self.config, self.call)
    # translate
# TranslatorOllama
