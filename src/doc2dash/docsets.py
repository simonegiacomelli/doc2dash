from __future__ import annotations

import os
import plistlib
import shutil
import sqlite3

from pathlib import Path

import attrs


@attrs.define(hash=True)
class DocSet:
    """
    Summary of docset path and parameters.
    """

    path: Path
    docs: Path
    plist: Path
    db_conn: sqlite3.Connection


def prepare_docset(
    source: Path,
    dest: Path,
    name: str,
    index_page: str | None,
    enable_js: bool,
    online_redirect_url: str | None,
) -> DocSet:
    """
    Create boilerplate files & directories and copy vanilla docs inside.

    Return a tuple of path to resources and connection to sqlite db.
    """
    resources = dest / "Contents" / "Resources"
    docs = resources / "Documents"
    os.makedirs(resources)

    db_conn = sqlite3.connect(resources / "docSet.dsidx")
    db_conn.row_factory = sqlite3.Row
    db_conn.execute(
        "CREATE TABLE searchIndex(id INTEGER PRIMARY KEY, name TEXT, "
        "type TEXT, path TEXT)"
    )
    db_conn.commit()

    plist_path = dest / "Contents" / "Info.plist"
    plist_cfg: dict[str, str | bool] = {
        "CFBundleIdentifier": name,
        "CFBundleName": name,
        "DocSetPlatformFamily": name.lower(),
        "DashDocSetFamily": "python",
        "DashDocSetDeclaredInStyle": "originalName",
        "isDashDocset": True,
        "isJavaScriptEnabled": enable_js,
    }
    if index_page is not None:
        plist_cfg["dashIndexFilePath"] = index_page
    if online_redirect_url is not None:
        plist_cfg["DashDocSetFallbackURL"] = online_redirect_url

    write_plist(plist_cfg, plist_path)

    shutil.copytree(source, docs)

    return DocSet(path=dest, docs=docs, plist=plist_path, db_conn=db_conn)


def add_icon(icon_data: bytes, dest: Path) -> None:
    """
    Add icon to docset
    """
    with (dest / "icon.png").open("wb") as f:
        f.write(icon_data)


def read_plist(full_path: Path) -> dict[str, str | bool]:
    with full_path.open("rb") as fp:
        return plistlib.load(fp)


def write_plist(plist: dict[str, str | bool], full_path: Path) -> None:
    with full_path.open("wb") as fp:
        plistlib.dump(plist, fp)
