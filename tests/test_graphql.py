from copy import deepcopy
import json
from unittest.mock import MagicMock, call, mock_open, patch
import requests
import pytest
from shopify_client.graphql import GraphQL
from tests.conftest import CopyingMock

@pytest.fixture
def graphql(mock_client):
    return GraphQL(client=mock_client)

def test_graphql_query(graphql, mock_client):
    mock_client.post.return_value = {"data": {"key": "value"}}
    response = graphql(query="query { key }")
    mock_client.post.assert_called_once_with("graphql.json", json={"query": "query { key }", "variables": None, "operationName": None})
    assert response == {"data": {"key": "value"}}

def test_graphql_query_with_query_name(graphql, mock_client):
    mock_query_content = "query { items { id } }"
    graphql.graphql_queries_dir = "queries"
    with patch("builtins.open", mock_open(read_data=mock_query_content)):
        mock_client.post.return_value = {"data": {"items": []}}
        response = graphql(query_name="test_query")
        mock_client.post.assert_called_once_with(
            "graphql.json",
            json={"query": mock_query_content, "variables": None, "operationName": None},
        )
        assert response == {"data": {"items": []}}

def test_graphql_query_with_variables(graphql, mock_client):
    mock_client.post.return_value = {"data": {"key": "value"}}
    variables = {"var1": "value1"}
    response = graphql(query="query { key }", variables=variables)
    mock_client.post.assert_called_once_with("graphql.json", json={"query": "query { key }", "variables": variables, "operationName": None})
    assert response == {"data": {"key": "value"}}

def test_query_paginated(graphql, mock_client):
    mock_client.post.side_effect = [
        {"data": {"pageInfo": {"hasNextPage": True, "endCursor": "cursor1"}}},
        {"data": {"pageInfo": {"hasNextPage": False}}}
    ]
    results = list(graphql(query="query { pageInfo { hasNextPage, endCursor } }", paginate=True))
    assert len(results) == 2
    assert results[0] == {"data": {"pageInfo": {"hasNextPage": True, "endCursor": "cursor1"}}}
    assert results[1] == {"data": {"pageInfo": {"hasNextPage": False}}}

def test_query_handles_http_error(graphql, mock_client, mocker):
    mock_client.post.side_effect = requests.exceptions.HTTPError("HTTP Error")
    response = graphql(query="query { key }")
    assert response == {}

def test_query_handles_json_error(graphql, mock_client):
    mock_client.post.side_effect = json.JSONDecodeError("JSON Decode Error", "", 0)
    response = graphql(query="query { key }")
    assert response == {}

def test_graphql_call(graphql, mock_client):
    mock_query_response = {"data": {"exampleField": "exampleValue"}}
    mock_client.post.return_value = mock_query_response

    # Call the GraphQL client like a function
    response = graphql("query { exampleField }")

    # Verify that the query method was called correctly
    mock_client.post.assert_called_once_with("graphql.json", json={'query': 'query { exampleField }', 'variables': None, 'operationName': None})

    # Assert the response is as expected
    assert response == mock_query_response

def test_graphql_query_paginated(graphql, mock_client, mocker):
    # Mock the paginated query method
    mock_paginated_response_1 = {
        "data": {
            "items": [1, 2, 3],
            "pageInfo": {
                "hasNextPage": True,
                "endCursor": "cursor-1"
            }
        }
    }
    mock_paginated_response_2 = {
        "data": {
            "items": [1, 2, 3],
            "pageInfo": {
                "hasNextPage": False,
                "endCursor": "cursor-2"
            }
        }
    }

    mock_client.post = CopyingMock(side_effect = [mock_paginated_response_1, mock_paginated_response_2])
    response = list(graphql(query="query { items { id } pageInfo { hasNextPage, endCursor } }", paginate=True))

    assert response == [mock_paginated_response_1, mock_paginated_response_2]
    assert mock_client.post.call_count == 2
    mock_client.post.assert_has_calls([
        call("graphql.json", json={"query": "query { items { id } pageInfo { hasNextPage, endCursor } }", "variables": {"cursor": None, "page_size": 100}, "operationName": None}),
        call("graphql.json", json={"query": "query { items { id } pageInfo { hasNextPage, endCursor } }", "variables": {"cursor": "cursor-1", "page_size": 100}, "operationName": None}),
    ])
