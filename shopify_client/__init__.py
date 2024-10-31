import logging
import time
from urllib.parse import urljoin

import requests

from shopify_client.hooks import rate_limit

from .endpoint import DraftOrdersEndpoint, Endpoint, OrdersEndpoint
from .graphql import GraphQL

logger = logging.getLogger(__name__)

SHOPIFY_API_VERSION = "2024-10"


class ShopifyClient(requests.Session):

    def __init__(self, api_url, api_token, api_version=SHOPIFY_API_VERSION, graphql_queries_dir=None):
        super().__init__()
        self.api_url = api_url
        self.api_version = api_version
        self.headers.update({"X-Shopify-Access-Token": api_token, "Content-Type": "application/json"})

        # Access
        self.storefront_access_tokens = Endpoint(client=self, endpoint="storefront_access_tokens")

        # Billing
        self.application_charges = Endpoint(client=self, endpoint="application_charges")
        self.application_credits = Endpoint(client=self, endpoint="application_credits")
        self.recurring_application_charges = Endpoint(client=self, endpoint="recurring_application_charges")

        # Customers
        self.customers = Endpoint(client=self, endpoint="customers", metafields=True)
        # self.customer_addresses = ShopifyEndpoint(client=self, endpoint="customer_addresses")

        # Discounts
        self.price_rules = Endpoint(client=self, endpoint="price_rules")
        self.discount_codes = Endpoint(client=self, endpoint="discount_codes")

        # Events
        self.events = Endpoint(client=self, endpoint="events")

        # Gift Cards
        self.gift_cards = Endpoint(client=self, endpoint="gift_cards")

        # Inventory
        self.inventory_items = Endpoint(client=self, endpoint="inventory_items")
        self.inventory_levels = Endpoint(client=self, endpoint="inventory_levels")
        self.locations = Endpoint(client=self, endpoint="locations", metafields=True)

        # Marketing Event
        self.marketing_events = Endpoint(client=self, endpoint="marketing_events")

        # Mobile Support
        self.mobile_platform_applications = Endpoint(client=self, endpoint="mobile_platform_applications")

        # Online Store
        self.articles = Endpoint(client=self, endpoint="articles", metafields=True)
        self.blogs = Endpoint(client=self, endpoint="blogs", metafields=True)
        self.pages = Endpoint(client=self, endpoint="pages", metafields=True)

        # Orders
        self.checkouts = Endpoint(client=self, endpoint="checkouts")
        self.draft_orders = DraftOrdersEndpoint(client=self, endpoint="draft_orders", metafields=True)
        self.orders = OrdersEndpoint(client=self, endpoint="orders")

        # Plus
        self.users = Endpoint(client=self, endpoint="users")

        # Products
        self.collects = Endpoint(client=self, endpoint="collects")
        self.collections = Endpoint(client=self, endpoint="collections", metafields=True)
        self.custom_collections = Endpoint(client=self, endpoint="custom_collections")
        self.products = Endpoint(client=self, endpoint="products", metafields=True)
        self.products.images = Endpoint(client=self, endpoint="products", sub_endpoint="images")
        self.product_images = Endpoint(client=self, endpoint="product_images", metafields=True)
        self.smart_collections = Endpoint(client=self, endpoint="smart_collections", metafields=True)
        self.variants = Endpoint(client=self, endpoint="variants", metafields=True)

        # Sales Channels
        self.collections_listings = Endpoint(client=self, endpoint="collections_listings")
        self.checkouts = Endpoint(client=self, endpoint="checkouts")
        self.product_listings = Endpoint(client=self, endpoint="product_listings")
        self.resource_feedback = Endpoint(client=self, endpoint="resource_feedback")

        # Shipping and Fulfillment
        self.assigned_fulfillment_orders = Endpoint(client=self, endpoint="assigned_fulfillment_orders")
        # TODO: Implement Fulfillment
        self.fulfillment_orders = Endpoint(client=self, endpoint="fulfillment_orders")
        self.carrier_services = Endpoint(client=self, endpoint="carrier_services")
        self.fulfillments = Endpoint(client=self, endpoint="fulfillments")
        self.fulfillment_services = Endpoint(client=self, endpoint="fulfillment_services")

        # Shopify Payments
        self.shopify_payments = Endpoint(client=self, endpoint="shopify_payments")

        # Store Properties
        self.countries = Endpoint(client=self, endpoint="countries")
        self.currencies = Endpoint(client=self, endpoint="currencies")
        self.policies = Endpoint(client=self, endpoint="policies")
        self.shipping_zones = Endpoint(client=self, endpoint="shipping_zones")
        self.shop = Endpoint(client=self, endpoint="shop", metafields=True)

        # Tender Transactions
        self.tender_transactions = Endpoint(client=self, endpoint="tender_transactions")

        # Webhooks
        self.webhooks = Endpoint(client=self, endpoint="webhooks")

        # GraphQL
        self.query = GraphQL(client=self, graphql_queries_dir=graphql_queries_dir)

        self.hooks["response"].append(rate_limit)

    def request(self, method, url, *args, **kwargs):
        response = super().request(method, urljoin(f"{self.api_url}/admin/api/{self.api_version}/", url), *args, **kwargs)
        logger.info(f"Requesting {method} {url}: {response.status_code}")
        return response

    def parse_response(self, response):
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.warning(f"Failed to execute request: {response.text}")
            raise e
        return response.json()