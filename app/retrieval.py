"""SQLite FTS5 retrieval layer for AfrekaOS Offline.

Indexes public SME operations markdown notes into a local SQLite FTS5 database
and provides simple full-text search. Standard library only.

The index is generated locally from public notes; it is not private data and
contains no customer/bank/payroll/tax records. No cloud database is used.

Schema
------
documents(doc_id, path, title, category, body)
docs_fts(body) -- FTS5 virtual table over body text, content linked to documents.

Path resolution
---------------
All paths default to repo-relative locations resolved against REPO_ROOT.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_DB_PATH = "data/afrekaos_fts.sqlite"
DEFAULT_SOURCE_DIRS = [
    "data/sme_operations",
    "data/language",
    "data/sources",
]

# Files we never index (safety).
_SKIP_DIRS = {".git", "model", "artifacts", "__pycache__", ".venv", "node_modules"}


def _resolve(path_str: str) -> Path:
    p = Path(path_str)
    if not p.is_absolute():
        p = REPO_ROOT / p
    return p


def _fts5_available(conn: sqlite3.Connection) -> bool:
    try:
        conn.execute("CREATE VIRTUAL TABLE _fts5_probe USING fts5(x)")
        conn.execute("DROP TABLE _fts5_probe")
        return True
    except sqlite3.OperationalError:
        return False


def _extract_title(text: str, fallback: str) -> str:
    """First H1 line, stripped; fallback to the file stem."""
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return fallback


def _category_from_path(file_path: Path, source_dirs: list[Path]) -> str:
    """Category is the source dir name the file sits under.

    Falls back to the immediate parent directory name, then 'general'.
    """
    fr = file_path.resolve()
    for d in source_dirs:
        dr = d.resolve()
        try:
            fr.relative_to(dr)
            return dr.name
        except ValueError:
            continue
    parent = file_path.parent.name
    return parent if parent else "general"


def _clean_body(text: str) -> str:
    """Collapse whitespace; keep the text searchable."""
    return re.sub(r"\s+", " ", text).strip()


def _iter_markdown_files(source_dirs: list[Path]) -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()
    for d in source_dirs:
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*.md")):
            # Skip private/hidden and forbidden directories.
            if any(part in _SKIP_DIRS for part in p.parts):
                continue
            if any(part.startswith(".") for part in p.parts):
                continue
            rp = p.resolve()
            if rp in seen:
                continue
            seen.add(rp)
            files.append(p)
    return files


def _doc_id_for(rel_path: Path) -> str:
    return rel_path.as_posix()


def _relative_path_for(f: Path, source_dirs: list[Path]) -> Path:
    """Compute a stable, readable relative path for a document.

    Tries repo-relative first; if the file is outside the repo (e.g. in tests),
    falls back to a path relative to the deepest common source-dir base, and
    finally to the resolved absolute path. Never raises.
    """
    fr = f.resolve()
    try:
        return fr.relative_to(REPO_ROOT.resolve())
    except ValueError:
        pass
    # Try each source dir as a base.
    for d in source_dirs:
        try:
            return fr.relative_to(d.resolve())
        except ValueError:
            continue
    # Last resort: absolute path.
    return fr


def build_index(
    source_dirs: Optional[list[str]] = None,
    db_path: Optional[str] = None,
) -> dict:
    """Build the SQLite FTS5 index from markdown notes.

    Returns a summary dict: {db_path, documents, source_dirs, fts5}.
    Raises RuntimeError if FTS5 is unavailable, and ValueError if no docs found.
    """
    db = _resolve(db_path or DEFAULT_DB_PATH)
    db.parent.mkdir(parents=True, exist_ok=True)
    if db.exists():
        db.unlink()

    dirs = [_resolve(d) for d in (source_dirs or DEFAULT_SOURCE_DIRS)]
    md_files = _iter_markdown_files(dirs)

    conn = sqlite3.connect(str(db))
    try:
        if not _fts5_available(conn):
            raise RuntimeError(
                "SQLite FTS5 is not available in this Python build. "
                "Install/compile SQLite with FTS5 enabled."
            )

        conn.execute(
            """
            CREATE TABLE documents (
                doc_id   TEXT PRIMARY KEY,
                path     TEXT,
                title    TEXT,
                category TEXT,
                body     TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE VIRTUAL TABLE docs_fts USING fts5(
                body,
                content='documents',
                content_rowid='rowid'
            )
            """
        )

        count = 0
        for f in md_files:
            try:
                text = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rel = _relative_path_for(f, dirs)
            doc_id = _doc_id_for(rel)
            title = _extract_title(text, f.stem)
            category = _category_from_path(f, dirs)
            body = _clean_body(text)
            conn.execute(
                "INSERT INTO documents (doc_id, path, title, category, body) "
                "VALUES (?, ?, ?, ?, ?)",
                (doc_id, rel.as_posix(), title, category, body),
            )
            conn.execute("INSERT INTO docs_fts (rowid, body) VALUES (last_insert_rowid(), ?)", (body,))
            count += 1

        conn.commit()

        if count == 0:
            raise ValueError(
                f"No markdown documents found under: {[str(d) for d in dirs]}"
            )

        return {
            "db_path": str(db),
            "documents": count,
            "source_dirs": [str(d) for d in dirs],
            "fts5": True,
        }
    finally:
        conn.close()


def _snippet(text: str, query: str, width: int = 180) -> str:
    """Return a text snippet around the first query term match (naive)."""
    if not text:
        return ""
    qlow = query.lower()
    tlow = text.lower()
    best = -1
    for term in re.split(r"\s+", qlow):
        term = term.strip()
        if len(term) < 2:
            continue
        idx = tlow.find(term)
        if idx != -1:
            best = idx
            break
    if best == -1:
        return text[:width] + ("..." if len(text) > width else "")
    start = max(0, best - 40)
    end = min(len(text), best + width - 40)
    snippet = text[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text):
        snippet = snippet + "..."
    return snippet


def search(
    query: str,
    limit: int = 5,
    db_path: Optional[str] = None,
) -> list[dict]:
    """Search the index. Returns a list of result dicts ranked by relevance."""
    db = _resolve(db_path or DEFAULT_DB_PATH)
    if not db.is_file():
        raise FileNotFoundError(
            f"Retrieval index not found at {db}. "
            "Run: python3 scripts/build_retrieval_index.py"
        )
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    try:
        # Build an FTS5 MATCH expression: quote terms, join with OR so a result
        # need not contain every term.
        terms = [t.strip() for t in re.split(r"\s+", query) if t.strip()]
        if not terms:
            return []
        match_expr = " OR ".join(f'"{t}"' for t in terms)
        rows = conn.execute(
            """
            SELECT d.doc_id, d.path, d.title, d.category, d.body,
                   bm25(docs_fts) AS rank
            FROM docs_fts
            JOIN documents d ON d.rowid = docs_fts.rowid
            WHERE docs_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (match_expr, limit),
        ).fetchall()
        results = []
        for r in rows:
            results.append(
                {
                    "doc_id": r["doc_id"],
                    "path": r["path"],
                    "title": r["title"],
                    "category": r["category"],
                    "snippet": _snippet(r["body"], query),
                    "rank": r["rank"],
                }
            )
        return results
    except sqlite3.OperationalError as exc:
        # FTS syntax errors should surface clearly.
        raise RuntimeError(f"Retrieval query failed: {exc}") from exc
    finally:
        conn.close()


def get_document(doc_id: str, db_path: Optional[str] = None) -> Optional[dict]:
    """Fetch a single document by doc_id, or None if not found."""
    db = _resolve(db_path or DEFAULT_DB_PATH)
    if not db.is_file():
        raise FileNotFoundError(f"Retrieval index not found at {db}.")
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    try:
        r = conn.execute(
            "SELECT doc_id, path, title, category, body FROM documents WHERE doc_id = ?",
            (doc_id,),
        ).fetchone()
        if r is None:
            return None
        return {
            "doc_id": r["doc_id"],
            "path": r["path"],
            "title": r["title"],
            "category": r["category"],
            "body": r["body"],
        }
    finally:
        conn.close()


def retrieval_summary(db_path: Optional[str] = None) -> dict:
    """Return a summary of the index: counts by category + total."""
    db = _resolve(db_path or DEFAULT_DB_PATH)
    if not db.is_file():
        raise FileNotFoundError(f"Retrieval index not found at {db}.")
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    try:
        total = conn.execute("SELECT COUNT(*) AS n FROM documents").fetchone()["n"]
        cats = conn.execute(
            "SELECT category, COUNT(*) AS n FROM documents GROUP BY category ORDER BY category"
        ).fetchall()
        return {
            "db_path": str(db),
            "documents": total,
            "categories": {row["category"]: row["n"] for row in cats},
            "fts5": True,
        }
    finally:
        conn.close()


__all__ = [
    "DEFAULT_DB_PATH",
    "DEFAULT_SOURCE_DIRS",
    "build_index",
    "search",
    "get_document",
    "retrieval_summary",
]
