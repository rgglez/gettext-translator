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

# -----------------------------------------------------------------------------

import json
import logging
import re

# -----------------------------------------------------------------------------

BATCH_SIZE = 100

LLM_PROMPT = """
You are an expert software localizer. Translate the user interface strings given by the user
from {src} into {dst}.

The input is a JSON array of objects with these fields:

- "n": numeric identifier of the item. Copy it unchanged into the answer.
- "id": the string to translate.
- "ctx" (optional): the context in which the string is used. Use it to choose the right meaning, do not translate it.
- "plural" (optional): the plural form of "id". "nplurals" is the number of plural forms {dst} uses in gettext.

Answer only with a JSON object of this form, without any other text:

{{"translations": [{{"n": 0, "msgstr": "Translated string"}}, {{"n": 1, "msgstr_plural": ["Form 0", "Form 1"]}}]}}

- Use "msgstr" for items without "plural".
- Use "msgstr_plural" for items with "plural": an array with exactly "nplurals" forms, in the order of the gettext
  Plural-Forms of {dst}.
- Keep placeholders (%s, %d, %(name)s, {{name}}), HTML tags, and leading or trailing whitespace exactly as they are.
- If you cannot translate an item, leave it out.
"""

# -----------------------------------------------------------------------------


def parse_json_response(text: str) -> list[dict]:
    """Extracts the list of results from an LLM answer, tolerating <think> blocks and ``` fences."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text).strip()
    data = json.loads(text)
    if isinstance(data, dict):
        data = data.get("translations", [])
    return [d for d in data if isinstance(d, dict)]
# parse_json_response

# -----------------------------------------------------------------------------


def translate_llm(items: list[dict], settings, call) -> list[dict]:
    """
    Translates the items in batches with an LLM.

    call(system_prompt, user_message) -> str sends one request to the model and returns its raw answer.
    """
    system_prompt = LLM_PROMPT.format(src=settings.src.display_name("en"), dst=settings.dst.display_name("en"))

    results = []
    for i in range(0, len(items), BATCH_SIZE):
        batch = items[i:i + BATCH_SIZE]
        user_message = json.dumps(batch, ensure_ascii=False)
        logging.debug("[ℹ️] Translation request: %s", user_message)
        try:
            response = call(system_prompt, user_message)
            logging.debug("[ℹ️] Raw API response: %s", response)
            results += parse_json_response(response)
        except Exception as e:  # pylint: disable=W0718
            logging.warning("[☠️] Batch of %d strings failed: %s", len(batch), e)
    # for

    return results
# translate_llm

# -----------------------------------------------------------------------------


def translate_plain(items: list[dict], translate_strings) -> list[dict]:
    """
    Adapter for backends that translate plain strings and know nothing about plurals.

    translate_strings(strings) receives a list of {"id": str, "ctx": str (optional)} and returns
    a list of translated strings (or None for failures) in the same order.
    """
    strings = []
    for item in items:
        string = {k: item[k] for k in ("id", "ctx") if k in item}
        strings.append(string)
        if "plural" in item:
            strings.append({**string, "id": item["plural"]})
    # for

    translated = iter(translate_strings(strings))

    results = []
    for item in items:
        singular = next(translated)
        if "plural" in item:
            plural = next(translated)
            # ponytail: form 0 = singular, other forms = plural. Wrong for languages with more than
            # two forms (ru, pl, ar...); use an LLM backend for those.
            forms = [plural] if item["nplurals"] == 1 else [singular] + [plural] * (item["nplurals"] - 1)
            results.append({"n": item["n"], "msgstr_plural": forms})
        else:
            results.append({"n": item["n"], "msgstr": singular})
    # for

    return results
# translate_plain
