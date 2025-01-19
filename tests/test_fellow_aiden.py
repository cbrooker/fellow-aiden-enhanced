import unittest
import json
from unittest.mock import patch, MagicMock
from fellow_aiden import FellowAiden

class TestFellowAiden(unittest.TestCase):

    def setUp(self):
        self.email = "test@example.com"
        self.password = "password"
        self.fellow_aiden = FellowAiden(self.email, self.password)

    @patch('fellow_aiden.requests.Session.post')
    def test_authentication_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = json.dumps({
            'accessToken': 'test_access_token',
            'refreshToken': 'test_refresh_token'
        }).encode('utf-8')
        mock_post.return_value = mock_response

        self.fellow_aiden.__auth()
        self.assertTrue(self.fellow_aiden._auth)
        self.assertEqual(self.fellow_aiden._token, 'test_access_token')

    @patch('fellow_aiden.requests.Session.get')
    def test_device_fetch_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = json.dumps([{
            'id': 'test_brewer_id',
            'profiles': [],
            'displayName': 'Test Brewer'
        }]).encode('utf-8')
        mock_get.return_value = mock_response

        self.fellow_aiden._FellowAiden__device()
        self.assertEqual(self.fellow_aiden._brewer_id, 'test_brewer_id')
        self.assertEqual(self.fellow_aiden.get_display_name(), 'Test Brewer')

    @patch('fellow_aiden.requests.Session.post')
    def test_create_profile_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.content = json.dumps({'id': 'test_profile_id'}).encode('utf-8')
        mock_post.return_value = mock_response

        data = {'name': 'Test Profile'}
        self.fellow_aiden.create_profile(data)
        self.assertIn('test_profile_id', [profile['id'] for profile in self.fellow_aiden.get_profiles()])

    @patch('fellow_aiden.requests.Session.delete')
    def test_delete_profile_success(self, mock_delete):
        self.fellow_aiden._profiles = [{'id': 'test_profile_id'}]
        self.fellow_aiden.delete_profile_by_id('test_profile_id')
        mock_delete.assert_called_once()

if __name__ == '__main__':
    unittest.main()
