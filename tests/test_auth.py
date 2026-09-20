"""Sign Up / Sign In behaviour (uses a throwaway SQLite file per test)."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scheme_matcher import auth, db


class AuthTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name) / "users.db"

    def tearDown(self):
        self._tmp.cleanup()

    def sign_up(self, name="Asha Rao", email="asha@example.com", password="Passw0rd!x", confirm=None):
        return auth.sign_up(name, email, password, password if confirm is None else confirm, self.path)

    def test_sign_up_returns_public_user_only(self):
        user, error = self.sign_up()
        self.assertIsNone(error)
        self.assertEqual(set(user), {"id", "name", "email"})
        self.assertEqual(user["email"], "asha@example.com")

    def test_email_is_normalised_and_unique_case_insensitively(self):
        self.sign_up(email="  Asha@Example.com ")
        user, error = self.sign_up(email="ASHA@example.com")
        self.assertIsNone(user)
        self.assertIn("already exists", error)

    def test_validation_messages(self):
        cases = [
            (dict(name="   "), "name"),
            (dict(email="not-an-email"), "valid email"),
            (dict(password="short"), "at least"),
            (dict(confirm="different1!"), "do not match"),
        ]
        for kwargs, expected in cases:
            with self.subTest(kwargs=kwargs):
                user, error = self.sign_up(**kwargs)
                self.assertIsNone(user)
                self.assertIn(expected, error)

    def test_sign_in_success_and_failures(self):
        self.sign_up()
        user, error = auth.sign_in("ASHA@example.com", "Passw0rd!x", self.path)
        self.assertIsNone(error)
        self.assertEqual(user["name"], "Asha Rao")

        for email, password in [("asha@example.com", "wrong-pass"), ("nobody@example.com", "Passw0rd!x")]:
            with self.subTest(email=email):
                user, error = auth.sign_in(email, password, self.path)
                self.assertIsNone(user)
                self.assertEqual(error, "Incorrect email or password.")

        self.assertIn("enter your email", auth.sign_in("", "", self.path)[1])

    def test_password_is_stored_salted_and_hashed(self):
        self.sign_up(email="one@example.com")
        self.sign_up(email="two@example.com")
        one = db.get_user_by_email("one@example.com", self.path)
        two = db.get_user_by_email("two@example.com", self.path)
        self.assertNotIn("Passw0rd!x", str(one))
        self.assertNotEqual(one["password_hash"], two["password_hash"])  # same password, different salt
        self.assertTrue(auth.verify_password("Passw0rd!x", one["password_hash"], one["password_salt"]))
        self.assertFalse(auth.verify_password("Passw0rd!y", one["password_hash"], one["password_salt"]))

    def test_database_enforces_unique_email(self):
        db.create_user("A", "dup@example.com", "h", "s", self.path)
        with self.assertRaises(sqlite3.IntegrityError):
            db.create_user("B", "dup@example.com", "h", "s", self.path)


if __name__ == "__main__":
    unittest.main()
