import pytest
from shopify_client.endpoint import FulfillmentOrdersEndpoint


@pytest.fixture
def fulfillment_orders_endpoint(mock_client):
    return FulfillmentOrdersEndpoint(client=mock_client, endpoint="fulfillment_orders")


def test_cancel_fulfillment_order(fulfillment_orders_endpoint, mock_client):
    mock_client.request.return_value = {"result": "cancelled"}
    response = fulfillment_orders_endpoint.cancel(1)
    mock_client.request.assert_called_once_with(
        "POST", "fulfillment_orders/1/cancel.json"
    )
    assert response == {"result": "cancelled"}
