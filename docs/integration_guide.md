# Integration Guide

Step-by-step guide for integrating the Patent Alert API into your platform.

## Prerequisites

1. API key from Patent Alert API
2. HTTP client library (e.g., `requests` for Python, `axios` for Node.js)
3. Webhook endpoint (optional, for real-time alerts)

## Quick Integration

### Python Example

```python
import requests

API_KEY = "your_api_key_here"
BASE_URL = "https://api.patentalert.com/api/v1"

def get_expiring_patents(industry=None, date_range="next_30_days", limit=50):
    """Query expiring patents"""
    headers = {"X-API-Key": API_KEY}
    params = {
        "industry": industry,
        "date_range": date_range,
        "limit": limit,
        "branding": False  # Remove API branding for white-label
    }
    
    response = requests.get(
        f"{BASE_URL}/expirations",
        headers=headers,
        params=params
    )
    response.raise_for_status()
    return response.json()

# Usage
patents = get_expiring_patents(industry="biotech", limit=10)
for patent in patents["data"]:
    print(f"{patent['patent_id']}: {patent['title']}")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const API_KEY = 'your_api_key_here';
const BASE_URL = 'https://api.patentalert.com/api/v1';

async function getExpiringPatents(industry, dateRange = 'next_30_days', limit = 50) {
  try {
    const response = await axios.get(`${BASE_URL}/expirations`, {
      headers: {
        'X-API-Key': API_KEY
      },
      params: {
        industry,
        date_range: dateRange,
        limit,
        branding: false
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching patents:', error.response?.data || error.message);
    throw error;
  }
}

// Usage
getExpiringPatents('biotech', 'next_30_days', 10)
  .then(data => {
    data.data.forEach(patent => {
      console.log(`${patent.patent_id}: ${patent.title}`);
    });
  });
```

## Webhook Integration

### Setting Up Webhooks

```python
import requests

def register_webhook(webhook_url, secret=None):
    """Register webhook for patent expiration alerts"""
    headers = {"X-API-Key": API_KEY}
    data = {
        "url": webhook_url,
        "secret": secret,
        "events": ["patent.expired"]
    }
    
    response = requests.post(
        f"{BASE_URL}/webhooks",
        headers=headers,
        json=data
    )
    response.raise_for_status()
    return response.json()
```

### Receiving Webhooks

```python
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)
WEBHOOK_SECRET = "your_webhook_secret"

@app.route('/webhooks/patents', methods=['POST'])
def handle_webhook():
    """Handle incoming webhook"""
    # Verify signature
    signature = request.headers.get('X-Webhook-Signature', '')
    expected_sig = hmac.new(
        WEBHOOK_SECRET.encode(),
        request.data,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(f'sha256={expected_sig}', signature):
        return {'error': 'Invalid signature'}, 401
    
    # Process webhook
    payload = request.json
    event = payload['event']
    data = payload['data']
    
    if event == 'patent.expired':
        # Handle patent expiration
        process_patent_expiration(data)
    
    return {'status': 'ok'}, 200
```

## Error Handling

```python
import requests
import time

def get_patents_with_retry(max_retries=3):
    """Get patents with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            response = requests.get(
                f"{BASE_URL}/expirations",
                headers={"X-API-Key": API_KEY},
                timeout=30
            )
            
            if response.status_code == 429:
                # Rate limited - wait and retry
                retry_after = int(response.headers.get('Retry-After', 60))
                time.sleep(retry_after)
                continue
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            time.sleep(wait_time)
    
    raise Exception("Max retries exceeded")
```

## Rate Limit Handling

```python
def check_rate_limits(response):
    """Check and log rate limit information"""
    remaining = response.headers.get('X-RateLimit-Remaining')
    limit = response.headers.get('X-RateLimit-Limit')
    reset = response.headers.get('X-RateLimit-Reset')
    
    if remaining:
        print(f"Rate limit: {remaining}/{limit} remaining")
        if int(remaining) < 10:
            print("Warning: Approaching rate limit")
    
    return {
        'remaining': int(remaining) if remaining else None,
        'limit': int(limit) if limit else None,
        'reset': int(reset) if reset else None
    }
```

## Caching Strategy

```python
import redis
import json
from datetime import datetime, timedelta

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_patents(industry, date_range, cache_ttl=3600):
    """Get patents with caching"""
    cache_key = f"patents:{industry}:{date_range}"
    
    # Check cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Fetch from API
    patents = get_expiring_patents(industry, date_range)
    
    # Cache result
    redis_client.setex(
        cache_key,
        cache_ttl,
        json.dumps(patents)
    )
    
    return patents
```

## Best Practices

1. **Implement Caching**: Cache API responses to reduce API calls and improve performance
2. **Handle Rate Limits**: Monitor rate limit headers and implement backoff strategies
3. **Use Webhooks**: Prefer webhooks over polling for real-time updates
4. **Error Handling**: Implement robust error handling with retries and fallbacks
5. **Logging**: Log API calls for debugging and monitoring
6. **Security**: Store API keys securely (environment variables, secrets management)
7. **Testing**: Test integration with mock data before production deployment

## Support

For integration support:
- Email: youssofsallam25@gmail.com
- Documentation: https://docs.patentalert.com
- Status Page: https://status.patentalert.com

