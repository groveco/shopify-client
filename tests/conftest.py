from copy import deepcopy
from unittest.mock import Mock

from shopify_client import ShopifyClient
from shopify_client.endpoint import Endpoint
import pytest


@pytest.fixture
def mock_client(mocker):
    client = mocker.Mock()
    client.parse_response.side_effect = lambda x: x  # Just return the response data as-is
    return client

@pytest.fixture
def endpoint(mock_client):
    return Endpoint(client=mock_client, endpoint="test_endpoint")


@pytest.fixture
def shopify_client(mocker):
    return ShopifyClient(api_url="https://test-shop.myshopify.com", api_token="test-token")

# Create a new mock that will deepcopy the arguments passed to it
    # https://docs.python.org/3.7/library/unittest.mock-examples.html#coping-with-mutable-arguments
class CopyingMock(Mock):
    def __call__(self, *args, **kwargs):
        args = deepcopy(args)
        kwargs = deepcopy(kwargs)
        return super().__call__(*args, **kwargs)