import unittest
from unittest.mock import patch
from static_comments_app import routes, app

class CommentsRouteTestCase(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SERVICE_TOKEN'] = "my-token"
        self.app = app.test_client()

    @patch('static_comments_app.routes.create_github_pull_request')
    def test_create_pull_request_success(self, mock_create_pull):
        mock_create_pull.return_value = True
        response = self.app.post("/comment/my-token",
                                 data=dict(name='name',
                                           email="a@example.com",
                                           website="www.example.com",
                                           message="Great post",
                                           slug="My first post"))
        self.assertEqual(201, response.status_code)

    @patch('static_comments_app.routes.create_github_pull_request')
    def test_create_pull_request_failure(self, mock_create_pull):
        mock_create_pull.return_value = False
        response = self.app.post("/comment/my-token",
                                 data=dict(name='name',
                                           email="a@example.com",
                                           website="www.example.com",
                                           message="Great post",
                                           slug="My first post"))
        self.assertEqual(500, response.status_code)
