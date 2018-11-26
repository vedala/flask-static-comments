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

    @patch('static_comments_app.routes.generate_random_str', return_value="abcdef")
    @patch('github3.repository')
    @patch('github3.login')
    def test_github3_repository(self, mock_github3_login,
                                mock_github3_repository, mock_generate_random_str):
        mock_sha = MagicMock()
        mock_sha.return_value = "my-sha-str"
        mock_github3_repository.return_value \
            .ref.return_value \
            .object.return_value.sha = mock_sha
        routes.create_github_pull_request("my-github-token",
            "my-github-username", "my-github-repo-name", "my-slug",
            "content-line-1\ncontent-line-2\n")
        mock_github3_login.assert_called_once_with(token="my-github-token")
        self.assertEqual("my-sha-str", mock_sha())
        mock_generate_random_str.assert_called_once_with(16)

if __name__ == '__main__':
    unittest.main()
