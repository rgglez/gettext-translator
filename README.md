# gettext-translator

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/license/mit)
![GitHub all releases](https://img.shields.io/github/downloads/rgglez/gettext-translator/total)
![GitHub issues](https://img.shields.io/github/issues/rgglez/gettext-translator)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/rgglez/gettext-translator)
![GitHub stars](https://img.shields.io/github/stars/rgglez/gettext-translator?style=social)
![GitHub forks](https://img.shields.io/github/forks/rgglez/gettext-translator?style=social)

This program uses several cloud and local services to translate [gettext](https://www.gnu.org/software/gettext/) [PO](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html) files.

## Backends

Currently, this system works with the following backends:

- Microsoft Azure AI Translator.
- OpenAI ChatGPT.
- Helsinki-NLP OPUS multilingual using transformers.

## Features

- **Bulk Translation Mode**: Enhances efficiency by facilitating the translation of multiple text entries simultaneously. This mode is subject to availability by the backend.
- **Comprehensive Logging**: Logs detailed information for progress monitoring and debugging purposes.
- **Fuzzy Entry Exclusion**: Enables the option to omit 'fuzzy' entries from translation in `.po` files.
- **Flexible Configuration**: Supports providing the configuration either through command-line arguments, the enviroment, a `.yaml` or a `.env` file.

## Architecture

This software was designed with extensibility as a priority, so it's not restricted to a single service or provider. It is based on an auto-discovery plugin system, and users can create additional plugins as needed.

![class diagram](class_diagram.png "Class Diagram")

## Requirements

Check the `requirements.txt` files in the CLI program directory and in each of the plugin directories.

## Configuration

TODO

## Installation

### From source code

You can install the main CLI program and each plugin using `pip` from their respective root directories.

```
pip install .
```

## From PyPI

Once the system is more polished, packages will be published on PyPI. Stay tuned for updates.

## Usage

To use `gettext-translator` as a command-line tool, see the `README.md` file in each plugin's directory for examples:

- [Azure AI Translator](translators/gettext-translator-azure/README.md) backend (remote API).
- [OpenAI ChatGPT](translators/gettext-translator-chatgpt/README.md) backend (remote API).
- [MarianMT](translators/gettext-translator-marianmt/README.md) backend (local).
- [NLLB](translators/gettext-translator-nllb/README.md) backend (local).

### Information about the plugins

You can view helpful information about the plugins, such as which configuration options specific to each one must be passed in the `--plugin-options` parameter. For example:

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

## Logging

The script logs detailed information about the files being processed, the backend's output and more.

## Notes

* It is recommended that you learn about [gettext](https://www.gnu.org/software/gettext/) and the [format of PO files](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html).
* Why gettext?
  * It uses full strings in the original language as keys. This is the most relevant reason, as it means you don't have to search for abstract keys like `page.title.hello` or `item.specification`. While that approach may work for a few strings, it becomes complicated with hundreds of thousands of them.
  * The original key string is used as a fallback. If a translation doesn't exist, the original string is displayed.
  * It's a tried and trusted GNU standard.
* This software was inspired by [pescheckit/python-gpt-po](https://github.com/pescheckit/python-gpt-po).
* **This software is work in progress**

## License

Copyright 2025 Rodolfo González González.

Licensed under [Apache version 2.0](https://www.apache.org/licenses/LICENSE-2.0). Please read the [LICENSE](LICENSE) file.
