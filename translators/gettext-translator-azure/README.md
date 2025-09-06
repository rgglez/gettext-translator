# gettext-translator-azure

Azure AI Translator implementation for `gettext-translator-service`.

## Usage from gettext-translator

```bash
python gettext_translator.py --backend azure --plugin_options="{\"apikey\":\"brown-fox\", \"location\":\"westus3\"}" --src en --dst es_MX --po /path/to/example/messages.po
```

This command translates the `messages.po` file from English into Mexican Spanish (es_MX), using the provided Azure AI Translator key in the `westus3` location.

## Loading the plugin

```python
from translator_service import load_plugins

plugins = load_plugins()
impl_cls = plugins["TranslatorAzure"]
impl = impl_cls()
impl.connect()
```

## Notes

- You can find information about Microsoft Azure AI Translator [here](https://learn.microsoft.com/en-us/azure/ai-services/translator/overview).


## License

Copyright 2025 Rodolfo González González.

Licensed under [Apache version 2.0](https://www.apache.org/licenses/LICENSE-2.0). Please read the [LICENSE](LICENSE) file.
