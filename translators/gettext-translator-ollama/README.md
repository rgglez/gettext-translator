# gettext-translator-ollama

Ollama backend for [gettext-translator](https://github.com/rgglez/gettext-translator).

## Usage from gettext-translator

```bash
gettext-translator --backend ollama --config ollama-sample.yaml --src en --dst de_DE --po /path/to/example/messages.po
```

This command translates the `messages.po` file from English into German.

## Configuration

* `ollama` the address:port of the Ollama server. For example: "127.0.0.1:11434"
* `model` the model you want to use. See the recommended models below.
* `temperature` optional. Default: 0.1.

Thinking is disabled for thinking models (qwen3...), it slows the translation down and doesn't improve it.

## Installation

```bash
pip install "gettext-translator[ollama]"
```

## Recommended Models for Ollama (2026)

For 2026, model names in Ollama have been standardized following the version and parameter size nomenclature. Here is the exact list of commands you should run based on your needs and hardware:

### 1. The Multilingual Standard (Recommended)

Currently the most balanced model for translation and general tasks:

* **qwen2.5:14b**
* **Note:** If version 3 is already available in your region: **qwen3:14b**.

### 2. Specialized in Translation (High Fidelity)

If you are looking for maximum grammatical precision, Google released specific variants within the Gemma 3 family.

* For most PCs: **translategemma:12b**
* For lightweight devices (laptops): **translategemma:4b**
* Maximum quality (Requires +24GB VRAM): **translategemma:27b**

### 3. The Meta "All-Rounder"

Ideal if you need the model to be very fast and understand complex instructions in English and Spanish perfectly.

* Balanced version: **llama3.2:3b**
* Powerful version: **llama4:8b** (The latest version of the Llama series in 2026).

### Summary

| Ideal Use Case | Exact Name for Ollama | RAM/VRAM Requirement |
| --- | --- | --- |
| **Technical Translation** | `qwen2.5:14b` | 16 GB |
| **Literary Translation** | `translategemma:12b` | 12 GB |
| **Fast/Mobile Translation** | `gemma3:4b` | 8 GB |
| **Very Long Contexts** | `mistral-nemo:12b` | 12 GB |

### Tip to save space

If you are not sure which one will give you the best result, you can use `pull` to download them in the background:

```bash
ollama pull qwen2.5:14b
ollama pull translategemma:12b
```

and then modify the YAML configuration file to try each one for your use cases.

## License

Copyright (C) 2026 Rodolfo González González.

Licensed under [GPL 3.0](https://www.gnu.org/licenses/gpl-3.0.html).
