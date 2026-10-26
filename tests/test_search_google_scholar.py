import os
import unittest
from unittest.mock import AsyncMock, patch

os.environ.setdefault("SEARCHAPI_API_KEY", "test-key")

import mcp_server_refactored


class SearchGoogleScholarTests(unittest.IsolatedAsyncioTestCase):
    async def test_basic_query(self):
        mock = AsyncMock(return_value={"organic_results": []})
        with patch.object(mcp_server_refactored.api_client, "request", mock):
            result = await mcp_server_refactored.search_google_scholar(q="rag")
        mock.assert_awaited_once_with(
            {"engine": "google_scholar", "q": "rag", "page": "1"}
        )
        self.assertEqual(result, {"organic_results": []})

    async def test_year_filters_and_page(self):
        mock = AsyncMock(return_value={})
        with patch.object(mcp_server_refactored.api_client, "request", mock):
            await mcp_server_refactored.search_google_scholar(
                q="rag", year_from="2020", year_to="2024", page="2"
            )
        mock.assert_awaited_once_with({
            "engine": "google_scholar", "q": "rag", "page": "2",
            "as_ylo": "2020", "as_yhi": "2024",
        })