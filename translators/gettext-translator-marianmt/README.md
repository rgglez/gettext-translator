# gettext-translator-marianmt

MarianMT implementation for `gettext-translator-service`.

## Usage from gettext-translator

```bash
python gettext_translator.py --backend marianmt --src en --dst zh_CN --po ../../example/messages.po
```

This command translates the `messages.po` file from English into Simplified Chinese from China (zh_CN), using the [Helsinki-NLP OPUS multilingual](https://huggingface.co/Helsinki-NLP) models processesing 100 translations per batch. This plugin runs locally.

## Configuration

None for the moment.

## Loading the plugin

```python
from gettext_translator_service import load_plugins

plugins = load_plugins()
impl_cls = plugins["TranslatorMarianMT"]
impl = impl_cls()
impl.connect()
```

## License

Copyright (C) 2026 Rodolfo González González.

Licensed under [GPL 3.0](https://www.gnu.org/licenses/gpl-3.0.html).