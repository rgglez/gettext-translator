# my-library

This is the core library defining the `TranslatorService` interface and the plugin loader.

## Usage
```python
from translator_service import load_plugins

plugins = load_plugins()
impl_cls = plugins["translator_azure", "translator_chatgpt"]
impl = impl_cls()
impl.connect()
