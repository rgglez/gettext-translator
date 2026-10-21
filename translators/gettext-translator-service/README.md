# gettext-translator-service

Plugin interface for [gettext-translator](https://github.com/rgglez/gettext-translator): the `TranslatorService` base class, the plugin loader and helpers to write backends.

## Writing a plugin

A plugin is a package that subclasses `TranslatorService` and registers it under the `gettext_translator_service.plugins` entry point group. The entry point name is the value of `--backend`.

```toml
[project.entry-points."gettext_translator_service.plugins"]
mybackend = "gettext_translator_mybackend:TranslatorMyBackend"
```

The options in the YAML file given with `--config` are available as attributes of `self.config`, along with the command line options (`src` and `dst` are [langcodes](https://pypi.org/project/langcodes/) `Language` objects). Values like `"env:MY_VAR"` are read from the environment. Options listed in `REQUIRES_CONFIG` are checked before the plugin runs.

```python
from gettext_translator_service import TranslatorService, translate_llm


class TranslatorMyBackend(TranslatorService):
    REQUIRES_CONFIG: list[str] = ["apikey", "model"]

    def configure(self):
        # Called once, before translate(): connect, load the model...
        self.client = MyClient(self.config.apikey)

    def call(self, system_prompt, user_message):
        return self.client.complete(self.config.model, system_prompt, user_message)

    def translate(self, items):
        return translate_llm(items, self.config, self.call)
```

### The translate() contract

`translate()` receives a list of items, one per unique string:

```python
{"n": 0, "id": "Open"}
{"n": 1, "id": "Payment", "ctx": "Invoice"}
{"n": 2, "id": "One file", "plural": "%d files", "nplurals": 2}
```

and returns a list of results, in any order, referring to the items by `n`:

```python
{"n": 0, "msgstr": "Öffnen"}
{"n": 2, "msgstr_plural": ["Eine Datei", "%d Dateien"]}
```

Items that couldn't be translated may be left out. `gettext-translator` validates every result (placeholders, HTML tags, number of plural forms) and discards the invalid ones.

### Helpers

- `translate_llm(items, settings, call)`: for LLM backends. Builds the prompt, sends the items in batches of 100 through `call(system_prompt, user_message) -> str` and parses the JSON answers.
- `translate_plain(items, translate_strings)`: for machine translation backends that translate plain strings and know nothing about plurals. `translate_strings` receives a list of `{"id", "ctx"?}` and returns the translations in the same order (`None` for failures).
- `parse_json_response(text)`: parses an LLM answer, tolerating `<think>` blocks and Markdown fences.

## License

Copyright (C) 2026 Rodolfo González González.

Licensed under [GPL 3.0](https://www.gnu.org/licenses/gpl-3.0.html).
