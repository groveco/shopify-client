import json
import requests
import pytest
from shopify_client.graphql import GraphQL

@pytest.fixture
def graphql(mock_client):
    return GraphQL(client=mock_client)

def test_graphql_query(graphql, mock_client):
    mock_client.post.return_value = {"data": {"key": "value"}}
    response = graphql.query(query="query { key }")
    mock_client.post.assert_called_once_with("graphql.json", json={"query": "query { key }", "variables": None, "operationName": None})
    assert response == {"data": {"key": "value"}}

def test_graphql_query_with_variables(graphql, mock_client):
    mock_client.post.return_value = {"data": {"key": "value"}}
    variables = {"var1": "value1"}
    response = graphql.query(query="query { key }", variables=variables)
    mock_client.post.assert_called_once_with("graphql.json", json={"query": "query { key }", "variables": variables, "operationName": None})
    assert response == {"data": {"key": "value"}}

def test_query_paginated(graphql, mock_client):
    mock_client.post.side_effect = [
        {"data": {"pageInfo": {"hasNextPage": True, "endCursor": "cursor1"}}},
        {"data": {"pageInfo": {"hasNextPage": False}}}
    ]
    results = list(graphql.query_paginated(query="query { pageInfo { hasNextPage, endCursor } }"))
    assert len(results) == 2
    assert results[0] == {"data": {"pageInfo": {"hasNextPage": True, "endCursor": "cursor1"}}}
    assert results[1] == {"data": {"pageInfo": {"hasNextPage": False}}}

def test_query_handles_http_error(graphql, mock_client, mocker):
    mock_client.post.side_effect = requests.exceptions.HTTPError("HTTP Error")
    response = graphql.query(query="query { key }")
    assert response == {}

def test_query_handles_json_error(graphql, mock_client):
    mock_client.post.side_effect = json.JSONDecodeError("JSON Decode Error", "", 0)
    response = graphql.query(query="query { key }")
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
