# gettext-translator

[![License](https://img.shields.io/badge/GitHub-GPL--3.0-informational)](https://www.gnu.org/licenses/gpl-3.0.html)
![GitHub all releases](https://img.shields.io/github/downloads/rgglez/gettext-translator/total)
![GitHub issues](https://img.shields.io/github/issues/rgglez/gettext-translator)
![GitHub commit activity](https://img.shields.io/github/commit-activity/y/rgglez/gettext-translator)
![GitHub stars](https://img.shields.io/github/stars/rgglez/gettext-translator?style=social)
![GitHub forks](https://img.shields.io/github/forks/rgglez/gettext-translator?style=social)

This program uses several cloud and local AI models to translate [gettext](https://www.gnu.org/software/gettext/) [PO](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html) files.

## Backends and how to use

To use `gettext-translator` as a command-line tool, see the `README.md` file in each plugin's directory for examples:

Currently this system works with the following backends:

- [Azure AI Translator](translators/gettext-translator-azure/README.md) backend (remote API, several models).
- [OpenAI ChatGPT](translators/gettext-translator-chatgpt/README.md) backend (remote API, several models).
- [MarianMT](translators/gettext-translator-marianmt/README.md) backend (local model).
- [NLLB](translators/gettext-translator-nllb/README.md) backend (local model).

Again, refer to each plugin's `README.md` file listed above to view usage examples.

## Architecture

This software was designed with extensibility as a priority, so it's not restricted to a single service or provider. It is based on an auto-discovery plugin system, and users can create additional plugins as needed.

![class diagram](class_diagram.png "Class Diagram")

## Requirements

See the `requirements.txt` files in the CLI program directory and in each of the plugin directories.

## Installation

### From source code

You can install the main CLI program and each plugin using `pip` from their respective root directories.

```
pip install .
```
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

## Notes

* It is recommended that you learn about [gettext](https://www.gnu.org/software/gettext/) and the [format of PO files](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html).
* Why gettext?
  * It uses full strings in the original language as keys. This is the most relevant reason, as it means you don't have to search for abstract keys like `page.title.hello` or `item.specification`. While that approach may work for a few strings, it becomes complicated with hundreds or thousands of them.
  * The original key string is used as a fallback. If a translation doesn't exist, the original string is displayed.
  * It's a tried and trusted GNU standard.
* This software was inspired by [pescheckit/python-gpt-po](https://github.com/pescheckit/python-gpt-po).

## License

Copyright (C) 2026 Rodolfo González González.

Licensed under [GPL 3.0](https://www.gnu.org/licenses/gpl-3.0.html).