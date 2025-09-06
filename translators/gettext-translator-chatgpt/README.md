# gettext-translator-chatgpt

ChatGPT API implementation for `gettext-translator-service`.

## Usage from gettext-translator

```bash
python gettext_translator.py --backend chatgpt --plugin_options="{\"model\":\"gpt-4o-mini\", \"apikey\":\"red-fox\"}" --src en --dst fr_CA --po /path/to/example/messages.po
```

This command translates the `messages.po` file from English into Canadian French (fr_CA), using the provided OpenAI API key, using the `gpt-4o-mini` model processesing 100 translations per batch. Very good results are produced by this model, which is a cheap one.

## Loading the plugin

```python
from translator_service import load_plugins

plugins = load_plugins()
impl_cls = plugins["TranslatorChatGPT"]
impl = impl_cls()
impl.connect()
```

## Notes

- You can find the name of the OpenAI ChatGPT models and their pricing [here](https://openai.com/api/pricing/).

## License

Copyright 2025 Rodolfo González González.

Licensed under [Apache version 2.0](https://www.apache.org/licenses/LICENSE-2.0). Please read the [LICENSE](LICENSE) file.
