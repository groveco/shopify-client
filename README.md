# shopify-client
Python client for Shopify REST &amp; GraphQL  API
## Installation

```bash
pip install -e git+https://github.com/groveco/shopify-client@main#egg=shopify_client
```

## Usage

### REST API

```python
from shopify_client import ShopifyClient

# Initialize the client
client = ShopifyClient(api_url='your_api_url', api_token='your_token', api_version='your_api_version')

# Get a list of products
products = client.products.all()

# Get only specific fields
products = client.products.all(fields="id,title")

# Get limited amount of products
products = client.products.all(limit=20)

# Use pagination
for page in client.products.all(paginate=True, limit=100)
    print(page)

# Get specific product by id
product = client.products.get(resource_id=1234)

# List product metafields for product id
metafields = client.products.metafields.all(resource_id=1234)

# Get speficic metafield by id
metafield = client.products.metafields.all(resource_id=1234, sub_resource_id=5678)

# Create a product
data = {"product":{"title":"Burton Custom Freestyle 151","body_html":"<strong>Good snowboard!</strong>","vendor":"Burton","product_type":"Snowboard","status":"draft"}}
product = client.products.create(json=data)

# Update product
product = client.products.create(resource_id=1234, json=data)

# Delete product
deleted = client.products.delete(resource=1234)

# Count of products
count = client.products.count()

# Cancel order
order = client.orders.cancel(resource_id=1234)

# Close order
order = client.orders.close(resource_id=1234)

```

### GraphQL API

```python
# Initialize the client
client = ShopifyClient(api_url='your_api_url', api_token='your_token', api_version='your_api_version', grapgql_queries_dir="queries")

# queries/listProducts.graphql
query products($page_size: Int = 100) {
  products(first: $page_size) {
    nodes {
      id
      title
    }
  }
}


# List products
response = client.query(query_name="listProducts")

# Limit page size
response = client.query(query, variables={"page_size": 20})

# Use pagination. 
# Note that "pageIngo" block with at least "hasNextPage" & "startCursor" is required
# $cursor value should be passed as "after" parameter
query = '''
query products($page_size: Int = 100, $cursor: String) {
  products(first: $page_size, after: $cursor) {
    nodes {
      id
      title
    }
    pageInfo {
      hasNextPage
      startCursor
    }
  }
}
'''
for page in client.query(query=query, paginate=True)
    print(page)
```

