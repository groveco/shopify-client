from unittest.mock import MagicMock
import requests

from shopify_client.hooks import rate_limit
import pytest

@pytest.fixture
def mock_connection():
    """Fixture to create a mock connection object."""
    return MagicMock()

@pytest.fixture
def initial_response(mock_connection):
    """Fixture to create an initial response object."""
    response = requests.Response()
    response.status_code = 429
    response.headers = {"retry-after": "2"}
    response.request = requests.Request("GET", "https://api.example.com/resource").prepare()
    response.request.headers["X-Retry-Count"] = 0
    response.connection = mock_connection
    return response

def test_rate_limit_retries_on_429(monkeypatch, initial_response, mock_connection):
    """Test that the rate_limit function retries on a 429 response."""
    new_response = requests.Response()
    new_response.status_code = 200  # Successful response to stop the retry loop
    new_response.request = initial_response.request
    mock_connection.send.return_value = new_response
    
    monkeypatch.setattr("time.sleep", lambda x: None)

    final_response = rate_limit(initial_response)

    assert final_response.status_code == 200
    assert mock_connection.send.call_count == 1
    assert final_response.request.headers["X-Retry-Count"] == 1

def test_rate_limit_stops_after_max_retries(monkeypatch, initial_response, mock_connection):
    failed_response = requests.Response()
    failed_response.status_code = 429
    failed_response.request = initial_response.request
    failed_response.connection = mock_connection
    
    mock_connection.send.return_value = failed_response

    monkeypatch.setattr("time.sleep", lambda x: None)

    final_response = rate_limit(initial_response)

    assert final_response.status_code == 429
    assert mock_connection.send.call_count == 5
    assert final_response.request.headers["X-Retry-Count"] == 5