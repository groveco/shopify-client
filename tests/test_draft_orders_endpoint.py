import pytest
from shopify_client.endpoint import DraftOrdersEndpoint

@pytest.fixture
def draft_orders_endpoint(mock_client):
    return DraftOrdersEndpoint(client=mock_client, endpoint="draft_orders")

def test_complete_draft_order(draft_orders_endpoint, mock_client):
    mock_client.request.return_value = {"result": "completed"}
    response = draft_orders_endpoint.complete(1)
    mock_client.request.assert_called_once_with("PUT", "draft_orders/1/complete.json")
    assert response == {"result": "completed"}

def test_send_invoice(draft_orders_endpoint, mock_client):
    mock_client.request.return_value = {"result": "invoice_sent"}
    response = draft_orders_endpoint.send_invoice(1)
    mock_client.request.assert_called_once_with("PUT", "draft_orders/1/send_invoice.json")
    assert response == {"result": "invoice_sent"}
