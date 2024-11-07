import logging
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class Endpoint(object):
    def __init__(self, client, endpoint, sub_endpoint=None, metafields=False):
        self.client = client
        self.endpoint = endpoint
        self.sub_endpoint = sub_endpoint
        
        if metafields:
            self.metafields = Endpoint(client=client, endpoint=self.endpoint, sub_endpoint="metafields")

    def __prepare_params(self, **params):
        flatted_params = []
        for key, value in params.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    flatted_params.append(
                        (f"{key}[{k}]", v)    
                    )
            elif isinstance(value, list):
                for v in value:
                    flatted_params.append(
                        (f"{key}[]", v)
                    )
            else:
                flatted_params.append((key, value))
        
        return flatted_params

    def __build_url(self, resource_id=None, sub_resource_id=None, action=None, **params):
        url = self.endpoint
        
        if resource_id:
            url = f"{url}/{resource_id}"

        if self.sub_endpoint:
            assert resource_id, "Resource ID is required for sub-endpoints"
            url = f"{url}/{self.sub_endpoint}"

        if sub_resource_id:
            assert self.sub_endpoint, "Sub-endpoint is required for sub-resource ID"
            url = f"{url}/{sub_resource_id}"

        if action:
            url = f"{url}/{action}"
        
        flatted_params = self.__prepare_params(**params)
        
        return f"{url}.json{'?' + urlencode(flatted_params) if flatted_params else ''}"
    
    def __paginate(self, url):
        next_url = url
        while next_url:
            response = self.client.get(next_url)
            yield self.client.parse_response(response)
            next_url = response.links.get("next", {}).get("url")

    # Public methods
    def get(self, resource_id, **params):
        url = self.__build_url(resource_id=resource_id, **params)
        return self.client.parse_response(self.client.get(url))
    
    def create(self, json: dict, **params):
        url = self.__build_url(**params)
        return self.client.parse_response(self.client.post(url, json=json))

    def update(self, resource_id, json, **params):
        url = self.__build_url(resource_id=resource_id, **params)
        return self.client.parse_response(self.client.put(url, json=json))

    def delete(self, resource_id, **params):
        url = self.__build_url(resource_id=resource_id, **params)
        resp = self.client.delete(url)
        return resp.ok
    
    def all(self, paginate=False, **params):
        url = self.__build_url(**params)
        if paginate:
            return self.__paginate(url)
        else:
            return self.client.parse_response(self.client.get(url))
        
    def action(self, action, resource_id, method="GET", **params):
        url = self.__build_url(resource_id=resource_id, action=action, **params)
        return self.client.parse_response(self.client.request(method, url, **params))
    
    def count(self, resource_id=None, **params):
        return self.action("count", resource_id=resource_id, **params)


class OrdersEndpoint(Endpoint):

    def __init__(self, client, endpoint):
        super().__init__(client, endpoint, metafields=True)
        
        self.transactions = Endpoint(client=client, endpoint=endpoint, sub_endpoint="transactions")
        self.risks = Endpoint(client=client, endpoint=endpoint, sub_endpoint="risks")
        self.refunds = Endpoint(client=client, endpoint=endpoint, sub_endpoint="refunds")

    def cancel(self, resource_id, **params):
        return self.action("cancel", resource_id=resource_id, method="POST", **params)
    
    def close(self, resource_id, **params):
        return self.action("close", resource_id=resource_id, method="POST", **params)
    
    def open(self, resource_id, **params):
        return self.action("open", resource_id=resource_id, method="POST", **params)
    

class DraftOrdersEndpoint(Endpoint):

    def complete(self, resource_id, **params):
        return self.action("complete", resource_id=resource_id, method="PUT", **params)
    
    def send_invoice(self, resource_id, **params):
        return self.action("send_invoice", resource_id=resource_id, method="PUT", **params)
    

class FulfillmentOrdersEndpoint(Endpoint):

    def __init__(self, client, endpoint):
        super().__init__(client, endpoint, metafields=True)

        self.fulfillment_request = Endpoint(client=client, endpoint=endpoint, sub_endpoint="fulfillment_request")

    def cancel(self, resource_id, **params):
        return self.action("cancel", resource_id=resource_id, method="POST", **params)