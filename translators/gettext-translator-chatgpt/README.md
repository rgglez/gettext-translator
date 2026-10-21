# gettext-translator-chatgpt

ChatGPT API backend for [gettext-translator](https://github.com/rgglez/gettext-translator).

## Usage from gettext-translator

```bash
gettext-translator --backend chatgpt --config sample-chatgpt.yaml --src en --dst fr_CA --po /path/to/example/messages.po
```

This command translates the `messages.po` file from English into Canadian French (fr_CA), using the provided OpenAI API key, using the `gpt-4o-mini` model processing 100 translations per batch. Very good results are produced by this model, which is a cheap one. See the [chatgpt-sample.yaml](chatgpt-sample.yaml) configuration file for the example.

## Configuration

* `apikey`
  - Your OpenAI ChatGPT API key.
  - Or, if you prefix the string with "env:", the value of the environment variable with the same name will be used. Example: apikey="env:MY_OPENAI_API_KEY" and then in the shell ```export MY_OPENAI_API_KEY="sk-..."```.
* `model` the model you want to use. See the Notes below.

## Installation

```bash
pip install "gettext-translator[chatgpt]"
```

## Notes

- You can find the name of the OpenAI ChatGPT models and their pricing [here](https://openai.com/api/pricing/).
- Of course, you need an [OpenAI API key](https://platform.openai.com/settings/organization/api-keys).

## License

Copyright (C) 2026 Rodolfo González González.

Licensed under [GPL 3.0](https://www.gnu.org/licenses/gpl-3.0.html).
