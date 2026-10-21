"""
    AI-based Gettext automatic translator.
    Copyright (C) 2026 Rodolfo González González.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# -----------------------------------------------------------------------------

import json
import sqlite3

# -----------------------------------------------------------------------------


class TranslationCache:
    """
    Persistent cache of validated translations, stored in SQLite.

    scope identifies what produced the translation (backend, model, languages),
    so changing any of them doesn't reuse old results.
    A key is (ctx, msgid, msgid_plural, nplurals), a value is a str or a list of plural forms.
    """

    def __init__(self, path: str, scope: tuple) -> None:
        self.scope = json.dumps(scope)
        self.db = sqlite3.connect(path)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS translations ("
            " scope TEXT, ctx TEXT, msgid TEXT, plural TEXT, nplurals INTEGER, value TEXT,"
            " PRIMARY KEY (scope, ctx, msgid, plural, nplurals))"
        )
    # __init__

    # -------------------------------------------------------------------------

    def get(self, key: tuple):
        row = self.db.execute(
            "SELECT value FROM translations WHERE scope=? AND ctx=? AND msgid=? AND plural=? AND nplurals=?",
            (self.scope, *key),
        ).fetchone()
        return json.loads(row[0]) if row else None
    # get

    # -------------------------------------------------------------------------

    def put(self, key: tuple, value) -> None:
        with self.db:
            self.db.execute(
                "INSERT OR REPLACE INTO translations VALUES (?, ?, ?, ?, ?, ?)",
                (self.scope, *key, json.dumps(value, ensure_ascii=False)),
            )
    # put
# TranslationCache
