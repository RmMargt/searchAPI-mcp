import unittest
from unittest.mock import patch
from datetime import datetime

import mcp_server

FIXED_NOW = datetime(2023, 1, 1, 12, 0, 0)

class FixedDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        return FIXED_NOW

class GetCurrentTimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_default_output(self):
        with patch('mcp_server.datetime', FixedDateTime):
            result = await mcp_server.get_current_time()
        self.assertEqual(result['date'], '2023-01-01')
        self.assertEqual(result['target_date']['iso'], '2023-01-01')
        self.assertEqual(result['now']['iso'], '2023-01-01')

    async def test_non_zero_offset(self):
        with patch('mcp_server.datetime', FixedDateTime):
            result = await mcp_server.get_current_time(days_offset='3')
        self.assertEqual(result['date'], '2023-01-04')
        self.assertEqual(result['target_date']['iso'], '2023-01-04')

    async def test_invalid_offset(self):
        result = await mcp_server.get_current_time(days_offset='bad')
        self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main()
