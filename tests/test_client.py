import requests
import pytest


def test_client_initialization(shopify_client):
    assert shopify_client.headers["X-Shopify-Access-Token"] == "test-token"
    assert shopify_client.headers["Content-Type"] == "application/json"


def test_request_with_versioning(shopify_client, mocker):
    mock_request = mocker.patch(
        "requests.Session.request",
        return_value=mocker.Mock(status_code=200, json=lambda: {"result": "success"}),
    )
    response = shopify_client.request("GET", "products.json")
    assert response.json() == {"result": "success"}
    mock_request.assert_called_once_with(
        "GET", "https://test-shop.myshopify.com/admin/api/2024-10/products.json"
    )


def test_parse_response_success(shopify_client, mocker):
    mock_response = mocker.Mock(status_code=200, json=lambda: {"key": "value"})
    parsed = shopify_client.parse_response(mock_response)
    assert parsed == {"key": "value"}


def test_parse_response_error(shopify_client, mocker):
    mock_response = mocker.Mock(status_code=404, text="Not Found")
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
        "Not Found"
    )

    with pytest.raises(requests.exceptions.HTTPError):
        shopify_client.parse_response(mock_response)
