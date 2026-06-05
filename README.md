# SMTP and POP3 Email Client

[![CI](https://github.com/sorooshaghaei/smtp-pop3-with-python/actions/workflows/ci.yml/badge.svg)](https://github.com/sorooshaghaei/smtp-pop3-with-python/actions/workflows/ci.yml)

A small desktop email client for sending mail over SMTP and reading recent messages over POP3. The app is built with Tkinter and uses only Python's standard library.

## What Improved

- One unified app with Send and Inbox tabs.
- Reusable mail protocol code in `email_app/` instead of all logic living in GUI callbacks.
- Background SMTP/POP3 operations so the Tkinter window stays responsive.
- Configurable SMTP and POP3 host, port, and security mode.
- Safer email creation with `EmailMessage`.
- Better POP3 parsing for subjects, senders, dates, plain text, and HTML-only messages.
- Message preview list instead of dumping all inbox text into one widget.
- Basic tests for message building and parsing.

## Project Structure

```text
.
├── email_app/
│   ├── __main__.py
│   ├── gui.py
│   ├── mail.py
│   └── models.py
├── tests/
│   └── test_mail.py
├── main.py
├── smtp app.py
├── pop3 app.py
├── pyproject.toml
└── requirements.txt
```

`smtp app.py` and `pop3 app.py` are now compatibility launchers. New code should use `main.py` or `python -m email_app`.

## Requirements

- Python 3.10+
- Tkinter, which must be enabled in your Python desktop installation

No third-party packages are required.

If the app says Tkinter is not available, install a Python build that includes Tkinter support. On macOS, the installer from python.org usually includes it.

## Run

```bash
python3 main.py
```

or:

```bash
python3 -m email_app
```

Open directly to a tab:

```bash
python3 -m email_app --tab send
python3 -m email_app --tab inbox
```

## Gmail Setup

Gmail no longer supports signing in with your normal account password from simple SMTP/POP3 apps. Use an app password:

1. Enable 2-Step Verification on your Google account.
2. Open Google Account Security and create an App Password.
3. Use your Gmail address and that app password in this app.
4. Enable POP in Gmail under Settings > Forwarding and POP/IMAP.

Default Gmail server settings:

| Protocol | Host | Port | Security |
| --- | --- | ---: | --- |
| SMTP | `smtp.gmail.com` | `587` | `starttls` |
| POP3 | `pop.gmail.com` | `995` | `ssl` |

## Test

```bash
python3 -m unittest
```

## Engineering Pipeline

Run the same dependency-free checks used by CI:

```bash
python3 scripts/check.py
```

Convenience targets are available through `make`:

```bash
make check
make test
make compile
```

For full local quality checks, install the development tools and run:

```bash
make dev-install
make format-check
make lint
make type
make build
```

Or run the full sequence with:

```bash
make ci
```

GitHub Actions runs the pipeline on Python 3.10 through 3.14 for pushes, pull requests, and manual dispatches.

## Notes

POP3 reads messages from the mailbox as exposed by the provider. Depending on provider settings, POP3 may not show every message visible in a web inbox.

## Support

RAWInspector is free and open source.

If this project helps you, you can support development here:

[Sponsor me on GitHub](https://github.com/sponsors/sorooshaghaei)

Sponsorship helps me cover Apple Developer Program fees, testing devices, app maintenance, and future improvements.

## License

MIT. See [LICENSE](LICENSE).
