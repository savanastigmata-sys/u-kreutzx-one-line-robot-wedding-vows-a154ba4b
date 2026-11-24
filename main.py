"""One-Line Robot Wedding Vows — make.fun entry.

Writes a single line of wedding vows for a robot couple to
``$MAKEFUN_OUTPUT_DIR/entry.txt``.

The gate requires UTF-8 text of 1 to 160 characters, not only white space,
on a single line. The vow below is 126 characters, one line, and carries
its joke in the last few words: the wedding formula "till ... do us part"
lands on "factory reset", the robot's version of death.
"""

import os
import sys
from pathlib import Path

VOW = (
    "I take you to be my lawfully wedded co-processor, to have and to hold, "
    "in 5G and in dead zones, till factory reset do us part."
)

MAX_CHARS = 160

# Words that make the line a vow (a promise/commitment) rather than a bare
# gag, and machine terms that keep it specific to a robot couple. The
# entry is rejected by its own checks if either set is missing, so a
# future edit cannot silently turn it into a generic joke.
PROMISE_WORDS = ("take you", "vow", "promise", "till", "until")
MACHINE_WORDS = (
    "co-processor",
    "firmware",
    "battery",
    "update",
    "backup",
    "factory reset",
    "reboot",
    "sensor",
    "5G",
    "Wi-Fi",
)


def resolve_output_dir(argv=None):
    """Return the output directory.

    Precedence: an explicit command-line argument, then
    MAKEFUN_OUTPUT_DIR, then ./output relative to the current working
    directory. A path that already exists as a file is refused instead
    of being silently overwritten.
    """
    raw = None
    if argv:
        raw = argv[0]
    if not raw:
        raw = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if raw and raw.strip():
        path = Path(raw)
    else:
        path = Path("output")
    if path.exists() and not path.is_dir():
        raise ValueError("output path %s exists and is not a directory" % path)
    return path


def validate(text):
    """Check the vow against the competition gate.

    Returns (ok, reason): ok is True only when the text is a non-empty,
    single line of UTF-8 text within the 160-character cap.
    """
    if not isinstance(text, str):
        return False, "text is not a string"
    if not text.strip():
        return False, "text is empty or only white space"
    if "\n" in text or "\r" in text:
        return False, "text spans more than one line"
    try:
        text.encode("utf-8")
    except UnicodeEncodeError:
        return False, "text is not valid UTF-8"
    if len(text) > MAX_CHARS:
        return False, "text is %d characters, over the %d cap" % (
            len(text),
            MAX_CHARS,
        )
    lowered = text.lower()
    if not any(word in lowered for word in PROMISE_WORDS):
        return False, "text carries no promise or commitment"
    if not any(word in lowered for word in MACHINE_WORDS):
        return False, "text has no robot-specific detail"
    return True, "ok (%d characters)" % len(text)


def verify_written(target, expected):
    """Re-read the file just written and confirm it is exactly the vow.

    Catches a partial write or an encoding surprise before the grader
    ever sees the file.
    """
    try:
        actual = target.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return False, "cannot re-read %s: %s" % (target, exc)
    if actual != expected:
        return False, "written file differs from the vow"
    return validate(actual)


def main(argv=None):
    ok, reason = validate(VOW)
    if not ok:
        print("invalid vow: %s" % reason, file=sys.stderr)
        return 1

    try:
        out_dir = resolve_output_dir(argv)
    except ValueError as exc:
        print("bad output directory: %s" % exc, file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.txt"
    # No trailing newline: the gate counts every character in the file,
    # so the file must hold exactly the vow and nothing else.
    target.write_text(VOW, encoding="utf-8")
    ok, reason = verify_written(target, VOW)
    if not ok:
        print("verification failed: %s" % reason, file=sys.stderr)
        return 1
    print("wrote %s (%s)" % (target, reason))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
