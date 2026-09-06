import argparse
import unittest

from scripts import make_admin


class MakeAdminScriptTests(unittest.TestCase):
    def test_normalizes_email_selector(self):
        args = argparse.Namespace(email="  ME@Example.COM ", username=None, list_users=False)

        self.assertEqual(make_admin.normalize_selector(args), ("email", "me@example.com"))

    def test_normalizes_username_selector(self):
        args = argparse.Namespace(email=None, username="  code_runner ", list_users=False)

        self.assertEqual(make_admin.normalize_selector(args), ("username", "code_runner"))

    def test_list_users_has_no_selector(self):
        args = argparse.Namespace(email=None, username=None, list_users=True)

        self.assertIsNone(make_admin.normalize_selector(args))

    def test_password_needs_letter_and_digit(self):
        self.assertEqual(
            make_admin.validate_password("onlyletters"),
            "Password must contain at least one letter and one digit.",
        )

    def test_password_accepts_valid_value(self):
        self.assertIsNone(make_admin.validate_password("CodeRunner123"))

    def test_parser_accepts_set_password(self):
        args = make_admin.build_parser().parse_args(
            ["--email", "me@example.com", "--set-password", "--password", "CodeRunner123"]
        )

        self.assertTrue(args.set_password)

    def test_parser_accepts_check_password(self):
        args = make_admin.build_parser().parse_args(
            ["--username", "code_runner", "--check-password", "--password", "CodeRunner123"]
        )

        self.assertTrue(args.check_password)


if __name__ == "__main__":
    unittest.main()
