import unittest
import warnings
from unittest.mock import patch, MagicMock
from static_comments_app import routes
import github3
from requests.models import Response

class GithubTestCase(unittest.TestCase):

    @patch('github3.login')
    def test_github3_login(self, mock_github3_login):
        routes.create_github_pull_request("my-github-token",
            "my-github-username", "my-github-repo-name", "my-slug",
            "John Commenter", "content-line-1\ncontent-line-2\n",
            "2018-12-03 12:10:20", "j@example.com", "johnswebsite.com")
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
            "John Commenter", "content-line-1\ncontent-line-2\n",
            "2018-12-03 12:10:20", "j@example.com", "johnswebsite.com")

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
            "John Commenter", "content-line-1\ncontent-line-2\n",
            "2018-12-03 12:10:20", "j@example.com", "johnswebsite.com")

        mock_generate_random_str.assert_called_once_with(16)

    @patch('static_comments_app.routes.generate_random_str', return_value="abcdef")
    @patch('github3.login')
    def test_create_ref(self, mock_github3_login,
                        mock_generate_random_str):

        github_username = "my-github-username"
        github_repo_name = "my-github-repo-name"

        mock_repository = MagicMock()
        mock_github3_login.return_value.repository = mock_repository

        mock_ref = MagicMock()
        mock_repository.return_value.ref = mock_ref

        sha_str = "my-sha-str"
        mock_object = MagicMock(sha=sha_str)
        mock_ref.return_value.object = mock_object

        mock_create_ref = MagicMock()
        mock_repository.return_value.create_ref = mock_create_ref

        routes.create_github_pull_request("my-github-token",
            github_username, github_repo_name, "my-slug",
            "John Commenter", "content-line-1\ncontent-line-2\n",
            "2018-12-03 12:10:20", "j@example.com", "johnswebsite.com")

        mock_create_ref.assert_called_once_with(
            "refs/heads/jekyll_comments_abcdef", sha_str)

    @patch('static_comments_app.routes.generate_random_str', return_value="abcdef")
    @patch('github3.login')
    def test_create_file(self, mock_github3_login,
                        mock_generate_random_str):

        github_username = "my-github-username"
        github_repo_name = "my-github-repo-name"

        mock_repository = MagicMock()
        mock_github3_login.return_value.repository = mock_repository

        mock_ref = MagicMock()
        mock_repository.return_value.ref = mock_ref

        sha_str = "my-sha-str"
        mock_object = MagicMock(sha=sha_str)
        mock_ref.return_value.object = mock_object

        mock_create_ref = MagicMock()
        mock_repository.return_value.create_ref = mock_create_ref

        mock_create_file = MagicMock()
        mock_repository.return_value.create_file = mock_create_file

        mock_create_pull = MagicMock()
        mock_repository.return_value.create_pull = mock_create_pull

        routes.create_github_pull_request("my-github-token",
            github_username, github_repo_name, "my-slug",
            "John Commenter", "content-line-1\ncontent-line-2\n",
            "2018-12-03 12:10:20", "j@example.com", "johnswebsite.com")

        mock_create_pull.assert_called_once_with(
            "Comment submission",
            "master",
            "my-github-username:refs/heads/jekyll_comments_abcdef",
            "This pull request creates a data file to be used as comment")

    @patch('github3.login')
    def test_authentication_failure(self, mock_github3_login):

        mock_repository = MagicMock()
        mock_github3_login.return_value.repository = mock_repository

        response = MagicMock(spec=Response)
        response.status_code = 401
        response.content = "some content"
        response.json.return_value = "{}"
        mock_repository.side_effect = \
            github3.exceptions.AuthenticationFailed(response)

        retval = routes.create_github_pull_request("my-github-token",
            "my-github-username", "my-github-repo-name", "my-slug",
            "John Commenter", "content-line-1\ncontent-line-2\n",
            "2018-12-03 12:10:20", "j@example.com", "johnswebsite.com")
        self.assertEqual(False, retval)

    @patch('github3.login')
    def test_invalid_ref_call(self, mock_github3_login):

        mock_repository = MagicMock()
        mock_github3_login.return_value.repository = mock_repository

        mock_ref = MagicMock()
        mock_repository.return_value.ref = mock_ref

        response = MagicMock(spec=Response)
        response.status_code = 404
        response.content = "some content"
        response.json.return_value = "{}"
        mock_ref.side_effect = github3.exceptions.NotFoundError(response)

        retval = routes.create_github_pull_request("my-github-token",
            "my-github-username", "my-github-repo-name", "my-slug",
            "John Commenter", "content-line-1\ncontent-line-2\n",
            "2018-12-03 12:10:20", "j@example.com", "johnswebsite.com")

        self.assertEqual(False, retval)
        mock_ref.assert_called_once_with("heads/master")

    @patch('static_comments_app.routes.generate_random_str', return_value="abcdef")
    @patch('github3.login')
    def test_invalid_create_ref(self, mock_github3_login,
                                        mock_generate_random_str):

        mock_repository = MagicMock()
        mock_github3_login.return_value.repository = mock_repository

        mock_ref = MagicMock()
        mock_repository.return_value.ref = mock_ref

        sha_str = "my-sha-str"
        mock_object = MagicMock(sha=sha_str)
        mock_ref.return_value.object = mock_object

        mock_create_ref = MagicMock()
        mock_repository.return_value.create_ref = mock_create_ref

        response = MagicMock(spec=Response)
        response.status_code = 422
        response.content = "some content"
        response.json.return_value = "{}"
        mock_create_ref.side_effect = \
            github3.exceptions.UnprocessableEntity(response)

        retval = routes.create_github_pull_request("my-github-token",
            "my-github-username", "my-github-repo-name", "my-slug",
            "John Commenter", "content-line-1\ncontent-line-2\n",
            "2018-12-03 12:10:20", "j@example.com", "johnswebsite.com")

        self.assertEqual(False, retval)
        mock_create_ref.assert_called_once_with(
            "refs/heads/jekyll_comments_abcdef", sha_str)

    @patch('static_comments_app.routes.generate_random_str', return_value="abcdef")
    @patch('github3.login')
    def test_invalid_create_file(self, mock_github3_login,
                        mock_generate_random_str):

        mock_repository = MagicMock()
        mock_github3_login.return_value.repository = mock_repository

        mock_ref = MagicMock()
        mock_repository.return_value.ref = mock_ref

        sha_str = "my-sha-str"
        mock_object = MagicMock(sha=sha_str)
        mock_ref.return_value.object = mock_object

        mock_create_ref = MagicMock()
        mock_repository.return_value.create_ref = mock_create_ref

        mock_create_file = MagicMock()
        mock_repository.return_value.create_file = mock_create_file

        response = MagicMock(spec=Response)
        response.status_code = 404
        response.content = "some content"
        response.json.return_value = "{}"
        mock_create_file.side_effect = \
            github3.exceptions.NotFoundError(response)

        retval = routes.create_github_pull_request("my-github-token",
            "my-github-username", "my-github-repo-name", "my-slug",
            "John Commenter", "content-line-1\ncontent-line-2\n",
            "2018-12-03 12:10:20", "j@example.com", "johnswebsite.com")

        self.assertEqual(False, retval)
        mock_create_file.assert_called_once_with(
            "_data/jekyll_comments/my-slug/abcdef.yml",
            "Create a new comment abcdef.yml",
            b'name: John Commenter\nmessage: content-line-1\ncontent-line-2\n\ndate: 2018-12-03 12:10:20\ngravatar: 19c7cf93d7e33c17730e5fccd7f4ab2e\nwebsite: johnswebsite.com\n',
            "refs/heads/jekyll_comments_abcdef")
    @patch('static_comments_app.routes.generate_random_str', return_value="abcdef")
    @patch('github3.login')
    def test_invalid_create_pull(self, mock_github3_login,
                        mock_generate_random_str):

        mock_repository = MagicMock()
        mock_github3_login.return_value.repository = mock_repository

        mock_ref = MagicMock()
        mock_repository.return_value.ref = mock_ref

        sha_str = "my-sha-str"
        mock_object = MagicMock(sha=sha_str)
        mock_ref.return_value.object = mock_object

        mock_create_ref = MagicMock()
        mock_repository.return_value.create_ref = mock_create_ref

        mock_create_file = MagicMock()
        mock_repository.return_value.create_file = mock_create_file

        mock_create_pull = MagicMock()
        mock_repository.return_value.create_pull = mock_create_pull

        response = MagicMock(spec=Response)
        response.status_code = 422
        response.content = "some content"
        response.json.return_value = "{}"
        mock_create_pull.side_effect = \
            github3.exceptions.NotFoundError(response)

        retval = routes.create_github_pull_request("my-github-token",
            "my-github-username", "my-github-repo-name", "my-slug",
            "John Commenter", "content-line-1\ncontent-line-2\n",
            "2018-12-03 12:10:20", "j@example.com", "johnswebsite.com")

        self.assertEqual(False, retval)
        mock_create_pull.assert_called_once_with(
            "Comment submission",
            "master",
            "my-github-username:refs/heads/jekyll_comments_abcdef",
            "This pull request creates a data file to be used as comment")

if __name__ == '__main__':
    unittest.main()
