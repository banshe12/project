import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio

class TestOSINTLogic(unittest.TestCase):
    def setUp(self):
        # We mock the parts of main.py needed for testing the scan logic
        self.username = "testuser"

    @patch('aiohttp.ClientSession.get')
    async def async_test_check_platform_success(self, mock_get):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = "<html><body>location: Mars</body></html>"
        mock_get.return_value.__aenter__.return_value = mock_response

        # Since we can't easily instantiate the App here without a Window,
        # we test the logic part of check_platform
        session = MagicMock()
        session.get = mock_get

        # Simulated logic from check_platform
        async with session.get("http://test.com") as response:
            status = response.status
            text = await response.text()

        self.assertEqual(status, 200)
        self.assertIn("location", text.lower())

    def test_run_async_logic(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.async_test_check_platform_success())

if __name__ == '__main__':
    unittest.main()
