from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SecurityMode = Literal["ssl", "starttls", "none"]


@dataclass(frozen=True)
class SMTPSettings:
    host: str = "smtp.gmail.com"
    port: int = 587
    security: SecurityMode = "starttls"
    timeout: int = 30


@dataclass(frozen=True)
class POP3Settings:
    host: str = "pop.gmail.com"
    port: int = 995
    security: SecurityMode = "ssl"
    timeout: int = 30


@dataclass(frozen=True)
class Credentials:
    username: str
    password: str


@dataclass(frozen=True)
class OutgoingMessage:
    sender: str
    recipient: str
    subject: str
    body: str


@dataclass(frozen=True)
class InboxMessage:
    number: int
    sender: str
    subject: str
    date: str
    body: str
