"""PyInstaller entry point for the bundled Linux Laptop Guard runtime."""

from laptop_guard.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
