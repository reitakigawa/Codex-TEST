import unittest
from pathlib import Path

from project.app import app


class AppSmokeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = app.test_client()

    def test_top_page_renders(self) -> None:
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Personal Site', response.get_data(as_text=True))

    def test_twitter_login_unavailable_status(self) -> None:
        response = self.client.get('/auth/twitter/login')
        self.assertIn(response.status_code, (302, 503))

    def test_twitter_auth_available_endpoint(self) -> None:
        response = self.client.get('/auth/twitter/available')
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIn("available", payload)

    def test_me_requires_login(self) -> None:
        response = self.client.get('/me')
        self.assertIn(response.status_code, (302, 503))

    def test_me_page_renders_after_session_login(self) -> None:
        with self.client.session_transaction() as sess:
            sess["user"] = {"id": "1", "name": "Test User", "username": "testuser"}
        response = self.client.get('/me')
        self.assertEqual(response.status_code, 200)
        self.assertIn("@testuser", response.get_data(as_text=True))

    def test_all_templates_can_be_loaded(self) -> None:
        template_root = Path(app.root_path) / "templates"
        with app.app_context():
            for template_file in template_root.rglob("*.html"):
                rel_path = template_file.relative_to(template_root).as_posix()
                app.jinja_env.get_template(rel_path)


if __name__ == '__main__':
    unittest.main()
