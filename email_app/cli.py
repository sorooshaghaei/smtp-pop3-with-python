from __future__ import annotations

import argparse
from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="SMTP and POP3 Tkinter email client")
    parser.add_argument("--tab", choices=("send", "inbox"), default="send")
    args = parser.parse_args(argv)

    try:
        from .gui import EmailApp
    except ModuleNotFoundError as exc:
        if exc.name == "_tkinter":
            raise SystemExit(
                "Tkinter is not available in this Python installation. "
                "Install a Python build with Tkinter support to run the desktop app."
            ) from exc
        raise

    app = EmailApp(start_tab=args.tab)
    app.mainloop()
