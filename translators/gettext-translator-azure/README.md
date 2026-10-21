# gettext-translator-azure

Azure AI Translator backend for [gettext-translator](https://github.com/rgglez/gettext-translator).

## Usage from gettext-translator

```bash
gettext-translator --backend azure --config azure-sample.yaml --src en --dst es_MX --po /path/to/example/messages.po
```

This command translates the `messages.po` file from English into Mexican Spanish (es_MX), using the provided Azure AI Translator key in the `westus3` location. See the [azure-sample.yaml](azure-sample.yaml) configuration file for the example.

## Configuration

* `apikey`
  - your Azure translation API key.
  - Or, if you prefix the string with "env:", the value of the environment variable with the same name will be used. Example: apikey="env:MY_AZURE_API_KEY" and then in the shell ```export MY_AZURE_API_KEY="sk-..."```.
* `location` the location of the translation service.
* `endpoint` the endpoint of the translation service.

## Installation

```bash
pip install "gettext-translator[azure]"
```

## Notes

- Plural forms: this backend translates the singular and the plural `msgid` separately and uses the plural translation for every form except the first one. That is right for languages with two plural forms; for languages with more (Russian, Polish, Arabic...) use an LLM backend.
- You can find information about Microsoft Azure AI Translator [here](https://learn.microsoft.com/en-us/azure/ai-services/translator/overview).


## License

Copyright (C) 2026 Rodolfo González González.

Licensed under [GPL 3.0](https://www.gnu.org/licenses/gpl-3.0.html).