import json
import logging

import requests

logger = logging.getLogger(__name__)


class GraphQL:

    def __init__(self, client):
        self.client = client
        self.endpoint = "graphql.json"

    def __build_url(self, **params):
        return self.endpoint
    
    def __call__(self, *args, **kwargs):
        return self.__query(*args, **kwargs)

    def __query(self, query, variables=None, operation_name=None, paginate=False):
        if paginate:
            return self.__paginate(query, variables, operation_name)
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

        variables = variables or {}
        variables["page_size"] = page_size

        has_next_page = True
        cursor = None

        while has_next_page:
            variables["cursor"] = cursor
            response = self.__query(query, variables, operation_name)
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