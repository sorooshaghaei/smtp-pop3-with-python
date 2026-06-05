from __future__ import annotations

import poplib
import re
import smtplib
import ssl
from email import policy
from email.message import EmailMessage, Message
from email.parser import BytesParser
from html import unescape
from html.parser import HTMLParser

from .models import Credentials, InboxMessage, OutgoingMessage, POP3Settings, SMTPSettings


class EmailClientError(RuntimeError):
    """Raised when a mail operation fails at the application boundary."""


class _HTMLTextExtractor(HTMLParser):
    block_tags = {"br", "div", "li", "p", "tr"}

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in self.block_tags:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        self._parts.append(data)

    def text(self) -> str:
        return _normalize_whitespace(unescape("".join(self._parts)))


def build_email_message(message: OutgoingMessage) -> EmailMessage:
    email_message = EmailMessage()
    email_message["From"] = message.sender
    email_message["To"] = message.recipient
    email_message["Subject"] = message.subject
    email_message.set_content(message.body)
    return email_message


def send_email(
    settings: SMTPSettings,
    credentials: Credentials,
    message: OutgoingMessage,
) -> None:
    email_message = build_email_message(message)
    context = ssl.create_default_context()

    try:
        if settings.security == "ssl":
            with smtplib.SMTP_SSL(
                settings.host,
                settings.port,
                timeout=settings.timeout,
                context=context,
            ) as server:
                _smtp_login_and_send(server, credentials, email_message)
            return

        with smtplib.SMTP(settings.host, settings.port, timeout=settings.timeout) as server:
            server.ehlo()
            if settings.security == "starttls":
                server.starttls(context=context)
                server.ehlo()
            _smtp_login_and_send(server, credentials, email_message)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailClientError(f"Could not send email: {exc}") from exc


def fetch_messages(
    settings: POP3Settings,
    credentials: Credentials,
    limit: int = 10,
) -> list[InboxMessage]:
    if limit < 1:
        raise EmailClientError("Message limit must be at least 1.")

    mailbox: poplib.POP3 | poplib.POP3_SSL | None = None
    context = ssl.create_default_context()

    try:
        if settings.security == "ssl":
            mailbox = poplib.POP3_SSL(
                settings.host,
                settings.port,
                timeout=settings.timeout,
                context=context,
            )
        else:
            mailbox = poplib.POP3(settings.host, settings.port, timeout=settings.timeout)
            if settings.security == "starttls":
                mailbox.stls(context=context)

        mailbox.user(credentials.username)
        mailbox.pass_(credentials.password)
        count, _ = mailbox.stat()
        numbers = range(count, max(0, count - limit), -1)

        messages: list[InboxMessage] = []
        for number in numbers:
            _, lines, _ = mailbox.retr(number)
            raw_message = b"\r\n".join(lines)
            messages.append(parse_inbox_message(raw_message, number))
        return messages
    except (OSError, poplib.error_proto) as exc:
        raise EmailClientError(f"Could not fetch email: {exc}") from exc
    finally:
        if mailbox is not None:
            try:
                mailbox.quit()
            except (OSError, poplib.error_proto):
                mailbox.close()


def parse_inbox_message(raw_message: bytes, number: int = 0) -> InboxMessage:
    message = BytesParser(policy=policy.default).parsebytes(raw_message)
    return InboxMessage(
        number=number,
        sender=_header_text(message, "From", "(unknown sender)"),
        subject=_header_text(message, "Subject", "(no subject)"),
        date=_header_text(message, "Date", ""),
        body=extract_message_body(message),
    )


def extract_message_body(message: Message) -> str:
    plain_parts: list[str] = []
    html_parts: list[str] = []

    for part in message.walk():
        if part.is_multipart():
            continue
        if part.get_content_disposition() == "attachment":
            continue

        content_type = part.get_content_type()
        text = _part_to_text(part)
        if not text:
            continue
        if content_type == "text/plain":
            plain_parts.append(text)
        elif content_type == "text/html":
            html_parts.append(_html_to_text(text))

    if plain_parts:
        return _normalize_whitespace("\n\n".join(plain_parts))
    if html_parts:
        return _normalize_whitespace("\n\n".join(html_parts))
    return "(message has no readable text body)"


def _smtp_login_and_send(
    server: smtplib.SMTP,
    credentials: Credentials,
    email_message: EmailMessage,
) -> None:
    server.login(credentials.username, credentials.password)
    server.send_message(email_message)


def _header_text(message: Message, name: str, fallback: str) -> str:
    value = message.get(name)
    if value is None:
        return fallback
    return str(value)


def _part_to_text(part: Message) -> str:
    get_content = getattr(part, "get_content", None)
    try:
        content = get_content() if callable(get_content) else None
    except (AttributeError, LookupError, UnicodeError):
        content = None

    if isinstance(content, str):
        return content

    payload = part.get_payload(decode=True)
    if not isinstance(payload, bytes):
        return ""

    charset = part.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace")


def _html_to_text(value: str) -> str:
    parser = _HTMLTextExtractor()
    parser.feed(value)
    parser.close()
    return parser.text()


def _normalize_whitespace(value: str) -> str:
    lines = [line.strip() for line in value.replace("\r\n", "\n").split("\n")]
    text = "\n".join(line for line in lines if line)
    return re.sub(r"\n{3,}", "\n\n", text).strip()
