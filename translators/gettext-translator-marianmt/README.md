# gettext-translator-marianmt

MarianMT backend for [gettext-translator](https://github.com/rgglez/gettext-translator).

## Usage from gettext-translator

```bash
gettext-translator --backend marianmt --src en --dst zh_CN --po ../../example/messages.po
```

This command translates the `messages.po` file from English into Simplified Chinese from China (zh_CN), using the [Helsinki-NLP OPUS multilingual](https://huggingface.co/Helsinki-NLP) models processing 100 translations per batch. This plugin runs locally.

## Configuration

None for the moment.

## Installation

```bash
pip install "gettext-translator[marianmt]"
```

## Notes

- Plural forms: this backend translates the singular and the plural `msgid` separately and uses the plural translation for every form except the first one. That is right for languages with two plural forms; for languages with more (Russian, Polish, Arabic...) use an LLM backend.
* You might need to get a token from HuggingFace and set this environment variable in order to avoid limits:

```bash
export HF_TOKEN=hf_xxxxxxxxxxxxxxxxx
```

## License

Copyright (C) 2026 Rodolfo González González.

Licensed under [GPL 3.0](https://www.gnu.org/licenses/gpl-3.0.html).