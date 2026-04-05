import unittest

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


if __name__ == '__main__':
    unittest.main()
