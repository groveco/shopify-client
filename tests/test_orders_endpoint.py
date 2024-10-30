import pytest
from shopify_client.endpoint import OrdersEndpoint, Endpoint

@pytest.fixture
def orders_endpoint(mock_client):
    return OrdersEndpoint(client=mock_client, endpoint="orders")

def test_cancel_order(orders_endpoint, mock_client):
    mock_client.request.return_value = {"result": "cancelled"}
    response = orders_endpoint.cancel(1)
    mock_client.request.assert_called_once_with("POST", "orders/1/cancel.json")
    assert response == {"result": "cancelled"}

def test_transactions_sub_endpoint(orders_endpoint):
    assert isinstance(orders_endpoint.transactions, Endpoint)
    assert orders_endpoint.transactions.endpoint == "orders"
    assert orders_endpoint.transactions.sub_endpoint == "transactions"
