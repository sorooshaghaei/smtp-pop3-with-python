import unittest
from email.message import EmailMessage

from email_app.mail import build_email_message, parse_inbox_message
from email_app.models import OutgoingMessage


class MailTests(unittest.TestCase):
    def test_build_email_message_sets_headers_and_body(self) -> None:
        message = build_email_message(
            OutgoingMessage(
                sender="sender@example.com",
                recipient="receiver@example.com",
                subject="Hello",
                body="Body text",
            )
        )

        self.assertEqual(message["From"], "sender@example.com")
        self.assertEqual(message["To"], "receiver@example.com")
        self.assertEqual(message["Subject"], "Hello")
        self.assertIn("Body text", message.get_content())

    def test_parse_inbox_message_prefers_plain_text(self) -> None:
        email_message = EmailMessage()
        email_message["From"] = "sender@example.com"
        email_message["Subject"] = "Plain"
        email_message.set_content("Plain body")
        email_message.add_alternative("<p>HTML body</p>", subtype="html")

        parsed = parse_inbox_message(email_message.as_bytes(), number=12)

        self.assertEqual(parsed.number, 12)
        self.assertEqual(parsed.sender, "sender@example.com")
        self.assertEqual(parsed.subject, "Plain")
        self.assertEqual(parsed.body, "Plain body")

    def test_parse_inbox_message_falls_back_to_html(self) -> None:
        email_message = EmailMessage()
        email_message["From"] = "sender@example.com"
        email_message["Subject"] = "HTML"
        email_message.add_alternative("<p>Hello<br>world</p>", subtype="html")

        parsed = parse_inbox_message(email_message.as_bytes())

        self.assertEqual(parsed.body, "Hello\nworld")


if __name__ == "__main__":
    unittest.main()
