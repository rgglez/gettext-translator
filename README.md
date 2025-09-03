# gettext-translator

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/license/mit)
![GitHub all releases](https://img.shields.io/github/downloads/rgglez/gettext-translator/total)
![GitHub issues](https://img.shields.io/github/issues/rgglez/gettext-translator)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/rgglez/gettext-translator)

**This software is work in progress**

This program allows to translate [PO](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html) files, as defined by [gettext](https://www.gnu.org/software/gettext/) using different cloud and local services. Currently it works reasonabily well with Microsoft Azure AI Translator and OpenAI ChatGPT.

## Features

- **Bulk Translation Mode**: Enhances efficiency by facilitating the translation of multiple text entries simultaneously. This mode is subject to availability by the backend.
- **Comprehensive Logging**: Logs detailed information for progress monitoring and debugging purposes.
- **Fuzzy Entry Exclusion**: Enables the option to omit 'fuzzy' entries from translation in `.po` files.
- **Flexible Configuration**: Supports providing the configuration either through command-line arguments, the enviroment, a `.yaml` or a `.env` file.

## Architechture

This software was designed with extensibility as a priority, so as not to restrict it to a single service or provider.

It is based on an auto-discovery plugin system. Additional plugins can be created by users if needed.

More TODO

## Requirements

TODO

## Configuration

TODO

## Installation

TODO

## Usage

Use `gettext-translator` as a command-line tool.

### Information about the plugins

You can view some helpful information about the plugins, for instance, which
configuration options specific to each plugin must be passed in the
`--plugin-options` parameter. For example:

```bash
python gettext_translator.py --info --backend chatgpt
```

<pre>
{
  "REQUIRES": [
    "apikey",
    "model"
  ]
}
</pre>

```bash
python gettext_translator.py --info --backend azure
```

<pre>
{
  "REQUIRES_CONFIG": [
    "apikey",
    "location"
  ]
}
</pre>

### OpenAI's ChatGPT

```bash
python gettext_translator.py --backend chatgpt --plugin_options="{\"model\":\"gpt-4o-mini\", \"apikey\":\"red-fox\"}" --src en --dst es_MX --po /path/to/example/messages.po
```

This command translates the `messages.po` file from English into Mexican Spanish (es_MX), using the provided OpenAI API key, using the `gpt-4o-mini` model processesing 100 translations per batch. Very good results are produced by this model, which is a cheap one.

### Microsoft Azure AI Translator

```bash
python gettext_translator.py --backend azure --plugin_options="{\"apikey\":\"brown-fox\", \"location\":\"westus3\"}" --src en --dst es_MX --po /path/to/example/messages.po
```

This command translates the `messages.po` file from English into Mexican Spanish (es_MX), using the provided Azure AI Translator key in the `westus3` location.

## Logging

The script logs detailed information about the files being processed.

## Notes

* You can find the name of the OpenAI ChatGPT models and their pricing [here](https://openai.com/api/pricing/).
* You can find information about Microsoft Azure AI Translator [here](https://learn.microsoft.com/en-us/azure/ai-services/translator/overview).
* It is recommended that you learn about [gettext](https://www.gnu.org/software/gettext/) and the [format of PO files](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html).
* Why gettext?
  * First and most relevant reason: it uses the full strings in the original language as key, so you don't have to be searching for weird keys such as "page.title.hello" or "item.specification". If one translation doesn't exist, the original key string is used.
  * It's a GNU standard, tried and trusted.
* This software was inspired by [pescheckit/python-gpt-po](https://github.com/pescheckit/python-gpt-po).

## License

Copyright 2025 Rodolfo González González.

Licensed under [Apache version 2.0](https://www.apache.org/licenses/LICENSE-2.0). Please read the [LICENSE](LICENSE) file.
