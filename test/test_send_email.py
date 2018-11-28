import unittest
import warnings
from unittest.mock import patch, MagicMock, PropertyMock
from static_comments_app import routes
from requests.models import Response
import sendgrid
from python_http_client import exceptions as sg_exceptions

class SendEMailTestCase(unittest.TestCase):

    @patch('python_http_client.client.Client')
    @patch('sendgrid.SendGridAPIClient')
    def test_invalid_send_email(self, mock_sendgrid, mock_client):
        mock_sendgrid.return_value.client = mock_client
        post = mock_client.mail.send.post.return_value
        post.side_effect = sg_exceptions.HTTPError
        retval = routes.send_email("", "", "")
        self.assertEqual(False, retval)

if __name__ == '__main__':
    unittest.main()
