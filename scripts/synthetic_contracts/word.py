"""Export a .docx to PDF with Microsoft Word for macOS, through `osascript` (spec 2026-10-31 § 4.3).

The converter is Word itself (owner decision 6: no substitute renderer). Word is sandboxed: a
`save as` to a path outside its container never returns (measured 2026-10-31: AppleEvent timeout
-1712 after 2 minutes saving to /private/tmp). Writing inside Word's own container works with no
dialog (Task 6 Step 1 spike, 2026-10-31, Word 16.114.3: open + save-as-PDF of a two-line document in
about 1 s). So `export_pdf` copies the .docx into
`~/Library/Containers/com.microsoft.Word/Data/tmp/iladub-synthetic/` under a fresh unique name, has
Word open it, save it as PDF there and close it without saving, then moves the PDF out and deletes
the copy. Only the document it opened is closed; no other Word document is touched.

The converter used is recorded in `examples/synthetic-contracts/synthetic.ttl` as `syn:converter`.

Justified PROCEDURAL (CLAUDE.md § 8): process orchestration of an external renderer — document
generation, no decision. TIMEOUT_S is a wait bound for an external process, not a reading
tolerance. No reader may call it (A3).
"""
from __future__ import annotations

import shutil
import subprocess
import uuid
from pathlib import Path

WORD_APP = Path("/Applications/Microsoft Word.app")
CONTAINER_TMP = Path.home() / "Library/Containers/com.microsoft.Word/Data/tmp/iladub-synthetic"
TIMEOUT_S = 300


class WordFailed(Exception):
    pass


def _osa(script: str) -> str:
    r = subprocess.run(["osascript", "-e", script], capture_output=True, text=True,
                       timeout=TIMEOUT_S + 30)
    if r.returncode != 0:
        raise WordFailed(r.stderr.strip() or f"osascript exit {r.returncode}")
    return r.stdout.strip()


def word_version() -> str:
    return _osa('tell application "Microsoft Word" to get version')


def converter() -> str:
    return f"Microsoft Word {word_version()} via osascript"


def _q(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def export_pdf(docx: Path, pdf: Path) -> None:
    CONTAINER_TMP.mkdir(parents=True, exist_ok=True)
    stem = f"iladub-{uuid.uuid4().hex}"
    src, out = CONTAINER_TMP / f"{stem}.docx", CONTAINER_TMP / f"{stem}.pdf"
    shutil.copyfile(docx, src)
    try:
        _osa(f'''with timeout of {TIMEOUT_S} seconds
tell application "Microsoft Word"
  open file name (POSIX file "{_q(str(src))}" as text)
  set d to document "{src.name}"
  try
    save as d file name (POSIX file "{_q(str(out))}" as text) file format format PDF
  on error e
    close d saving no
    error e
  end try
  close d saving no
end tell
end timeout''')
        if not out.is_file():
            raise WordFailed(f"Word reported success but wrote no PDF for {docx}")
        Path(pdf).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(out), str(pdf))
    finally:
        src.unlink(missing_ok=True)
        out.unlink(missing_ok=True)
