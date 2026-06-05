import unittest
from contextlib import redirect_stdout
from io import StringIO

from email_app.cli import main


class CLITests(unittest.TestCase):
    def test_help_exits_before_importing_tkinter_gui(self) -> None:
        output = StringIO()

        with redirect_stdout(output), self.assertRaises(SystemExit) as error:
            main(["--help"])

        self.assertEqual(error.exception.code, 0)
        self.assertIn("SMTP and POP3 Tkinter email client", output.getvalue())


if __name__ == "__main__":
    unittest.main()
