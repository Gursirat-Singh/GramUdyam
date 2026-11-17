#!/usr/bin/env python3
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


def _ensure_django_available():
    try:
        import django  # noqa: F401
    except ImportError:
        # Fallback for air-gapped VM sandbox environment
        base = Path(__file__).resolve().parent
        for candidate in [
            base / ".vendor",
            base.parent / "artifacts" / "file_generation" / "ttl=63d" / "intermediate" / "vendor",
            base / "artifacts" / "file_generation" / "ttl=63d" / "intermediate" / "vendor",
        ]:
            if candidate.exists() and str(candidate) not in sys.path:
                sys.path.insert(0, str(candidate))
                break


def main():
    """Run administrative tasks."""
    _ensure_django_available()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
