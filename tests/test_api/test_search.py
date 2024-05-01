from datetime import datetime

import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from fastapi import status

from app.main import app  # Import your FastAPI app configuration

@pytest.mark.asyncio
@pytest.mark.parametrize("search_term, status_code", [
    ("", 422),  # Empty string, should fail
    ("a" * 101, 422),  # String longer than 100 chars, should fail
    ("validkeyword", 200),  # Valid input, should pass
])
async def test_search_term_validation(search_term, status_code):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/chats/search", params={"search_term": search_term})
        assert response.status_code == status_code

@pytest.mark.asyncio
@pytest.mark.parametrize("page_size, page, status_code", [
    (0, 1, 422),  # Zero page size, should fail
    (-1, 1, 422),  # Negative page size, should fail
    (10, 0, 422),  # Zero page, should fail (if pages are 1-indexed)
    (10, -1, 422),  # Negative page number, should fail
    (25, 1, 500),  # Valid pagination, should pass
])
async def test_pagination_validation(page_size, page, status_code):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/chats/search", params={
            "search_term": "test",
            "page_size": page_size,
            "page": page
        })
        assert response.status_code == status_code

@pytest.mark.asyncio
@pytest.mark.parametrize("search_term, expected_status", [
    ("valid", status.HTTP_200_OK),  # Valid search term
    ("", status.HTTP_422_UNPROCESSABLE_ENTITY),  # Empty string
    ("x" * 101, status.HTTP_422_UNPROCESSABLE_ENTITY),  # Exceeds maximum length
])
async def test_search_term_validation(search_term, expected_status):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/chats/search/all", params={"search_term": search_term})
        assert response.status_code == expected_status
        if response.status_code != status.HTTP_200_OK:
            assert "detail" in response.json()  # Ensure error details are provided

