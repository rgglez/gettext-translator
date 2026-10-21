# gettext-translator-gemini

Gemini API backend for [gettext-translator](https://github.com/rgglez/gettext-translator).

## Usage from gettext-translator

```bash
gettext-translator --backend gemini --config gemini-sample.yaml --src en --dst de_DE --po /path/to/example/messages.po
```

This command translates the `messages.po` file from English into German, using Gemini. See the [gemini-sample.yaml](gemini-sample.yaml) configuration file for the example.

## Configuration

* `apikey`
  - Your Gemini API key.
  - Or, if you prefix the string with "env:", the value of the environment variable with the same name will be used. Example: apikey="env:MY_GEMINI_API_KEY" and then in the shell ```export MY_GEMINI_API_KEY="the_api_key"```.
* `model` the model you want to use. See the Notes below.
* `temperature` optional parameter to control the fidelity of the translation. Default: 0.3.

## Installation

```bash
pip install "gettext-translator[gemini]"
```

## Notes

- You can find the name of the Gemini models and their pricing [here](https://ai.google.dev/gemini-api/docs/pricing?hl=es-419).
- Of course, you need a [Google AI Studio API key](https://aistudio.google.com/api-keys).
- There is a free layer for certain models, for example `gemini-2.5-flash-lite`. Otherwise, Google may require you to pay.
- `gemini-2.5-flash-lite` produces good results, as far as I have tested. It is available in the free layer.

## License

Copyright (C) 2026 Rodolfo González González.

Licensed under [GPL 3.0](https://www.gnu.org/licenses/gpl-3.0.html).
