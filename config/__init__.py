import sys
from pathlib import Path

try:
    import django  # noqa: F401
except ImportError:
    base = Path(__file__).resolve().parent.parent
    for candidate in [
        base / ".vendor",
        base.parent / "artifacts" / "file_generation" / "ttl=63d" / "intermediate" / "vendor",
        base / "artifacts" / "file_generation" / "ttl=63d" / "intermediate" / "vendor",
    ]:
        if candidate.exists() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
            break
