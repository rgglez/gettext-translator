# gettext-translator-azure

Azure AI Translator implementation for `gettext-translator-service`.

## Usage from gettext-translator

```bash
python gettext_translator.py --backend azure --config azure-sample.yaml --src en --dst es_MX --po /path/to/example/messages.po
```

This command translates the `messages.po` file from English into Mexican Spanish (es_MX), using the provided Azure AI Translator key in the `westus3` location. See the [azure-sample.yaml](azure-sample.yaml) configuration file for the example.

## Configuration

* `apikey`
  - your Azure translation API key.
  - Or, if you prefix the string with "env:", the value of the environment variable with the same name will be used. Example: apikey="env:MY_AZURE_API_KEY" and then in the shell ```export MY_AZURE_API_KEY="sk-..."```.
* `location` the location of the translation service.
* `endpoint` the endpoint of the translation service.

## Loading the plugin

```python
from gettext_translator_service import load_plugins

plugins = load_plugins()
impl_cls = plugins["TranslatorAzure"]
impl = impl_cls()
impl.connect()
```

## Notes

- You can find information about Microsoft Azure AI Translator [here](https://learn.microsoft.com/en-us/azure/ai-services/translator/overview).


## License

Copyright (C) 2026 Rodolfo González González.

Licensed under [GPL 3.0](https://www.gnu.org/licenses/gpl-3.0.html).