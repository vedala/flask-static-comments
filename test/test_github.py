import unittest
from unittest.mock import patch, MagicMock
from static_comments_app import routes
import github3

class GithubTestCase(unittest.TestCase):

    @patch('github3.login')
    def test_github3_login(self, mock_github3_login):
        routes.create_github_pull_request("my-github-token",
            "my-github-username", "my-github-repo-name", "my-slug",
            "content-line-1\ncontent-line-2\n")
        mock_github3_login.assert_called_once_with(token="my-github-token")

    @patch('github3.login')
    def test_github3_repository(self, mock_github3_login):

        github_username = "my-github-username"
        github_repo_name = "my-github-repo-name"

        mock_repository = MagicMock()
        mock_github3_login.return_value.repository = mock_repository

        mock_ref = MagicMock()
        mock_repository.return_value.ref = mock_ref

        routes.create_github_pull_request("my-github-token",
            github_username, github_repo_name, "my-slug",
            "content-line-1\ncontent-line-2\n")

        mock_repository.assert_called_once_with(github_username,
                                                github_repo_name)
        mock_ref.assert_called_once_with("heads/master")

    @patch('static_comments_app.routes.generate_random_str', return_value="abcdef")
    @patch('github3.login')
    def test_generate_random_str(self, mock_github3_login,
                                 mock_generate_random_str):
        github_username = "my-github-username"
        github_repo_name = "my-github-repo-name"

        routes.create_github_pull_request("my-github-token",
            github_username, github_repo_name, "my-slug",
            "content-line-1\ncontent-line-2\n")

        mock_generate_random_str.assert_called_once_with(16)

if __name__ == '__main__':
    unittest.main()
