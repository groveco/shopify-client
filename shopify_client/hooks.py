import time


def rate_limit(response, *args, **kwargs):
    max_retry_count = 5
    retry_count = int(response.request.headers.get("X-Retry-Count", 0))
    print(f"Response: {response}")
    
    if response.status_code == 429 and retry_count < max_retry_count:
        retry_after = int(response.headers.get("retry-after", 4))
        # print(f"Retry after: {retry_after}")
        time.sleep(retry_after)
        response.request.headers["X-Retry-Count"] = retry_count + 1
        new_response = response.connection.send(response.request)
        new_response.history.append(response)
        return rate_limit(new_response, *args, **kwargs)
    
    return response