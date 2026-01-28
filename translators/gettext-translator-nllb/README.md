# gettext-translator-nllb

NLLB implementation for `gettext-translator-service`.

## Usage from gettext-translator

```bash
python gettext_translator.py --backend nllb --src es --dst de_DE --config nllb-sample.yaml --po ../../example/messages.po
```

This command translates the `messages.po` file from Spanish into German from Germany (de_DE), using the [NLLB-200's 1.3B](https://huggingface.co/facebook/nllb-200-1.3B) model. This plugin runs locally.

## Configuration

* `model` is the model to be used. See below.

## Available models

- [NLLB-200's 3.3B variant](https://huggingface.co/facebook/nllb-200-3.3B): Use `nllb-200-3.3B`
- [NLLB-200's 1.3B variant](https://huggingface.co/facebook/nllb-200-1.3B): Use `nllb-200-1.3B`
- [NLLB-200's distilled 600M](https://huggingface.co/facebook/nllb-200-distilled-600M): Use: `nllb-200-distilled-600M`

## Loading the plugin

```python
from gettext_translator_service import load_plugins

plugins = load_plugins()
impl_cls = plugins["TranslatorNLLB"]
impl = impl_cls()
impl.connect()
```

## Notes

* In my tests, `nllb-200-1.3B` did the best contextual translation for the sample file. Bad results are obtained with the other models.
* You might need to [get a token from HuggingFace](https://huggingface.co/settings/tokens) and set this enviroment variable in order to avoid limits:

  ```bash
  export HF_TOKEN=hf_xxxxxxxxxxxxxxxxx
  ```

## License

Copyright (C) 2026 Rodolfo González González.

Licensed under [GPL 3.0](https://www.gnu.org/licenses/gpl-3.0.html).