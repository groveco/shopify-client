import requests
import pytest
from shopify_client import Endpoint, OrdersEndpoint, DraftOrdersEndpoint

@pytest.fixture
def mock_client(mocker):
    client = mocker.Mock()
    client.parse_response.side_effect = lambda x: x  # Just return the response data as-is
    return client

@pytest.fixture
def endpoint(mock_client):
    return Endpoint(client=mock_client, endpoint="test_endpoint")

def test_prepare_params(endpoint):
    params = {
        "simple": "value",
        "nested": {"key1": "value1", "key2": "value2"},
        "list": ["item1", "item2"]
    }
    expected = [
        ("simple", "value"),
        ("nested[key1]", "value1"),
        ("nested[key2]", "value2"),
        ("list[]", "item1"),
        ("list[]", "item2")
    ]
    result = endpoint._Endpoint__prepare_params(**params)
    assert result == expected

def test_build_url_basic(endpoint):
    url = endpoint._Endpoint__build_url(resource_id=1)
    assert url == "test_endpoint/1.json"

def test_build_url_with_params(endpoint):
    url = endpoint._Endpoint__build_url(resource_id=1, action="test", param="value")
    assert url == "test_endpoint/1/test.json?param=value"

def test_get(endpoint, mock_client):
    mock_client.get.return_value = {"result": "success"}
    response = endpoint.get(1, param="value")
    mock_client.get.assert_called_once_with("test_endpoint/1.json?param=value")
    assert response == {"result": "success"}

def test_create(endpoint, mock_client):
    mock_client.post.return_value = {"result": "created"}
    data = {"field": "value"}
    response = endpoint.create(json=data)
    mock_client.post.assert_called_once_with("test_endpoint.json", json=data)
    assert response == {"result": "created"}

def test_update(endpoint, mock_client):
    mock_client.put.return_value = {"result": "updated"}
    data = {"field": "new_value"}
    response = endpoint.update(1, json=data, param="value")
    mock_client.put.assert_called_once_with("test_endpoint/1.json?param=value", json=data)
    assert response == {"result": "updated"}

def test_delete(endpoint, mock_client):
    mock_client.delete.return_value.ok = True
    response = endpoint.delete(1, param="value")
    mock_client.delete.assert_called_once_with("test_endpoint/1.json?param=value")
    assert response is True

def test_paginated_calls(endpoint, mock_client, mocker):
    mock_client.parse_response.side_effect = lambda x: x.json()

    first_page_response = mocker.Mock(spec=requests.Response)
    first_page_response.json.return_value = {"items": [1, 2, 3]}
    first_page_response.links = {"next": {"url": "https://test-shop.myshopify.com/admin/api/2024-10/test_endpoint.json?page=2"}}
    
    second_page_response = mocker.Mock(spec=requests.Response)
    second_page_response.json.return_value = {"items": [4, 5, 6]}
    second_page_response.links = {}  # No next link on the second page (end of pagination)

    mock_client.get.side_effect = [first_page_response, second_page_response]

    # Call the all() method with pagination enabled
    results = list(endpoint.all(paginate=True))

    # Check that the combined results match what we expect
    expected_items = [1, 2, 3, 4, 5, 6]
    actual_items = [item for page in results for item in page.get("items", [])]

    assert actual_items == expected_items
    assert len(results) == 2  # We should have two pages of results
    assert mock_client.get.call_count == 2  # Ensure get was called twice
