# gettext-translator-marianmt

Azure implementation for `translator-service`.

## Usage
```python
from translator_service import load_plugins

plugins = load_plugins()
impl_cls = plugins["TranslatorAzure"]
impl = impl_cls()
impl.connect()
