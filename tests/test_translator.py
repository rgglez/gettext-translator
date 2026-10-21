"""
Tests for the gettext translator, using a fake backend (no network).
"""

import polib
import pytest

from gettext_translator.cache import TranslationCache
from gettext_translator.gettext_translator import GettextTranslator
from gettext_translator.settings import Settings
from gettext_translator_service import TranslatorService, load_plugins, parse_json_response, translate_plain


class FakeService(TranslatorService):
    """Translates "x" into "[de] x", keeping placeholders. Records every request."""

    def __init__(self, settings, broken=False):
        super().__init__(settings)
        self.requests = []
        self.broken = broken

    def translate(self, items):
        self.requests.append(items)
        if self.broken:
            return [{"n": item["n"], "msgstr": "no placeholders"} for item in items]
        return translate_plain(items, lambda strings: ["[de] " + s["id"] for s in strings])


def write_po(path, body, lang="de_DE", nplurals=2):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        'msgid ""\nmsgstr ""\n'
        f'"Language: {lang}\\n"\n'
        f'"Plural-Forms: nplurals={nplurals}; plural=(n != 1);\\n"\n\n' + body,
        encoding="utf-8",
    )
    return path


def make_translator(tmp_path, po, cache=None, **kwargs):
    settings = Settings(po=[str(p) for p in po], src="es", dst="de", config=str(tmp_path / "none.yaml"), **kwargs)
    return GettextTranslator(FakeService(settings, kwargs.pop("broken", False)), cache)


def test_same_msgid_with_different_context(tmp_path):
    po = write_po(tmp_path / "a.po", 'msgctxt "a"\nmsgid "X"\nmsgstr ""\n\nmsgctxt "b"\nmsgid "X"\nmsgstr ""\n')
    translator = make_translator(tmp_path, [po])

    assert translator.translate()

    assert [e.msgstr for e in polib.pofile(str(po))] == ["[de] X", "[de] X"]
    assert [item["ctx"] for item in translator.service.requests[0]] == ["a", "b"]


def test_plurals(tmp_path):
    po = write_po(tmp_path / "a.po", 'msgid "One file"\nmsgid_plural "%d files"\nmsgstr[0] ""\nmsgstr[1] ""\n'
                  'msgstr[2] ""\n', nplurals=3)

    make_translator(tmp_path, [po]).translate()

    assert polib.pofile(str(po))[0].msgstr_plural == {0: "[de] One file", 1: "[de] %d files", 2: "[de] %d files"}


def test_plain_adapter_single_plural_form():
    results = translate_plain([{"n": 0, "id": "a", "plural": "b", "nplurals": 1}], lambda s: [x["id"] for x in s])
    assert results == [{"n": 0, "msgstr_plural": ["b"]}]


def test_ascribe_keeps_existing_comment(tmp_path):
    po = write_po(tmp_path / "a.po", '#. Developer note\nmsgid "X"\nmsgstr ""\n')

    make_translator(tmp_path, [po], ascribe=True).translate()

    assert polib.pofile(str(po))[0].comment == "Developer note\nAI-translated"


def test_lost_placeholder_is_discarded(tmp_path):
    po = write_po(tmp_path / "a.po", 'msgid "Hola <b>%s</b>"\nmsgstr ""\n')

    assert not make_translator(tmp_path, [po], broken=True).translate()

    assert polib.pofile(str(po))[0].msgstr == ""


def test_language_mismatch_leaves_file_untouched(tmp_path):
    po = write_po(tmp_path / "a.po", 'msgid "X"\nmsgstr ""\n', lang="fr")
    before = po.read_text(encoding="utf-8")

    make_translator(tmp_path, [po]).translate()

    assert po.read_text(encoding="utf-8") == before


def test_fuzzy_flag_removed(tmp_path):
    po = write_po(tmp_path / "a.po", '#, fuzzy\nmsgid "X"\nmsgstr "Y"\n')

    make_translator(tmp_path, [po], fuzzy=True).translate()

    assert not polib.pofile(str(po))[0].fuzzy


def test_directory_dedupe_and_cache(tmp_path):
    body = 'msgid "Shared"\nmsgstr ""\n'
    write_po(tmp_path / "locale" / "a.po", body)
    write_po(tmp_path / "locale" / "sub" / "b.po", body)
    cache = TranslationCache(str(tmp_path / "cache.db"), ("fake",))

    first = make_translator(tmp_path, [tmp_path / "locale"], cache=cache, dry_run=True)
    first.translate()
    assert [len(r) for r in first.service.requests] == [1]
    assert polib.pofile(str(tmp_path / "locale" / "a.po"))[0].msgstr == ""  # dry run saves nothing

    second = make_translator(tmp_path, [tmp_path / "locale"], cache=cache)
    assert second.translate()
    assert second.service.requests == []
    assert polib.pofile(str(tmp_path / "locale" / "sub" / "b.po"))[0].msgstr == "[de] Shared"


def test_output_directory(tmp_path):
    po = write_po(tmp_path / "locale" / "sub" / "a.po", 'msgid "X"\nmsgstr ""\n')

    make_translator(tmp_path, [tmp_path / "locale"], output=str(tmp_path / "out")).translate()

    assert polib.pofile(str(tmp_path / "out" / "sub" / "a.po"))[0].msgstr == "[de] X"
    assert polib.pofile(str(po))[0].msgstr == ""


def test_output_file_requires_single_input(tmp_path):
    a = write_po(tmp_path / "a.po", "")
    b = write_po(tmp_path / "b.po", "")

    with pytest.raises(ValueError):
        make_translator(tmp_path, [a, b], output=str(tmp_path / "x.po")).translate()


def test_parse_json_response():
    text = '<think>hmm</think>\n```json\n{"translations": [{"n": 0, "msgstr": "a"}]}\n```'
    assert parse_json_response(text) == [{"n": 0, "msgstr": "a"}]
    assert parse_json_response('[{"n": 1, "msgstr": "b"}, "junk"]') == [{"n": 1, "msgstr": "b"}]


def test_settings_yaml_env_and_cli_precedence(tmp_path, monkeypatch):
    config = tmp_path / "config.yaml"
    config.write_text('apikey: "env:TEST_KEY"\nmodel: "from-yaml"\ncontext: "yaml"\n', encoding="utf-8")
    monkeypatch.setenv("TEST_KEY", "secret")

    args = Settings.parse_cli_args(["--po", "a.po", "--dst", "de", "--config", str(config), "--context", "cli"])
    settings = Settings(**vars(args))

    assert (settings.apikey, settings.model, settings.context) == ("secret", "from-yaml", "cli")


def test_missing_required_config(tmp_path):
    class NeedsKey(FakeService):
        REQUIRES_CONFIG = ["apikey"]

    with pytest.raises(ValueError, match="apikey"):
        NeedsKey(Settings(po=["a.po"], config=str(tmp_path / "none.yaml")))


def test_installed_plugins_load():
    for name, cls in load_plugins().items():
        assert issubclass(cls, TranslatorService), name
