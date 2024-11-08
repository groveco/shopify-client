import json
import logging
import os

import requests

logger = logging.getLogger(__name__)


class GraphQL:

    def __init__(self, client, graphql_queries_dir=None):
        self.client = client
        self.endpoint = "graphql.json"
        self.graphql_queries_dir = graphql_queries_dir

    def __build_url(self, **params):
        return self.endpoint

    def __call__(self, *args, **kwargs):
        return self.__query(*args, **kwargs)

    def query_from_name(self, name):
        assert self.graphql_queries_dir, "GraphQL queries directory is not set"

        query_path = os.path.join(self.graphql_queries_dir, f"{name}.graphql")
        with open(query_path, "r") as f:
            return f.read()

    def __query(self, query=None, query_name=None, variables=None, operation_name=None, paginate=False, page_size=100):
        assert query or query_name, "Either 'query' or 'query_name' must be provided"

        if query is None and query_name:
            query = self.query_from_name(query_name)

        if paginate:
            return self.__paginate(query=query, variables=variables, operation_name=operation_name, page_size=page_size)
        try:
            response = self.client.post(
                self.__build_url(),
                json={"query": query, "variables": variables, "operationName": operation_name},
            )
            return self.client.parse_response(response)
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Failed to execute GraphQL query: {repr(e)}")
            return {}
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {repr(e)}")
            return {}

    def __paginate(self, query, variables=None, operation_name=None, page_size=100):
        assert "pageInfo" in query, "Query must contain a 'pageInfo' object to be paginated"
        assert "hasNextPage" in query[query.find("pageInfo"):], "Query must contain a 'hasNextPage' field in 'pageInfo' object"
        assert "endCursor" in query[query.find("pageInfo"):], "Query must contain a 'endCursor' field in 'pageInfo' object"

        variables = variables or {}
        variables["page_size"] = page_size

        has_next_page = True
        cursor = None

        while has_next_page:
            variables["cursor"] = cursor
            response = self.__query(query=query, variables=variables, operation_name=operation_name)
            page_info = self.__find_page_info(response)
            has_next_page = page_info.get("hasNextPage", False)
            cursor = page_info.get("endCursor", None)

            yield response

    def __find_page_info(self, response):
        # Recursively search for the pageInfo object in the response
        result = response.get("pageInfo")
        if result:
            return result

        for k, v in response.items():
            if isinstance(v, dict):
                result = self.__find_page_info(v)
                if result:
                    return result