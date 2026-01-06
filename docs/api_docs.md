# API Documentation

Complete API reference for the Patent Alert API.

## Base URL

```
https://api.patentalert.com/api/v1
```

## Authentication

All API requests require an API key in the `X-API-Key` header:

```
X-API-Key: your_api_key_here
```

## Rate Limits

- Default: 60 requests per minute, 10,000 requests per day
- Custom limits can be configured per partner
- Rate limit headers are included in responses:
  - `X-RateLimit-Limit`: Maximum requests per window
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset time (Unix timestamp)

## Endpoints

### Health Check

```http
GET /health
```

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00"
}
```

### Get Expiring Patents

```http
GET /api/v1/expirations
```

Query patents expiring in a specified date range.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `industry` | string | No | - | Industry filter (biotech, electronics, software, etc.) |
| `date_range` | string | No | next_30_days | Date range: next_7_days, next_30_days, next_90_days, next_365_days |
| `limit` | integer | No | 50 | Maximum results (1-1000) |
| `offset` | integer | No | 0 | Pagination offset |
| `branding` | boolean | No | true | Include API branding in response |

**Example Request:**
```bash
curl -X GET "https://api.patentalert.com/api/v1/expirations?industry=biotech&date_range=next_30_days&limit=10" \
  -H "X-API-Key: your_api_key_here"
```

**Response:**
```json
{
  "data": [
    {
      "patent_id": "US12345678",
      "title": "Novel Therapeutic Compound",
      "abstract": "A method for treating...",
      "expiration_date": "2024-12-31T00:00:00",
      "grant_date": "2004-12-31T00:00:00",
      "inventor": "Smith, John",
      "assignee": "Pharma Corp",
      "technology_area": "biotechnology",
      "summary": "AI-generated summary of the patent...",
      "relevance_score": 0.95,
      "powered_by": "Patent Alert API"
    }
  ],
  "count": 1,
  "limit": 10,
  "offset": 0,
  "total_estimated": 1
}
```

### Get Patent by ID

```http
GET /api/v1/expirations/{patent_id}
```

Get detailed information about a specific patent.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `patent_id` | string | Patent number (e.g., US12345678) |

**Example Request:**
```bash
curl -X GET "https://api.patentalert.com/api/v1/expirations/US12345678" \
  -H "X-API-Key: your_api_key_here"
```

**Response:**
```json
{
  "patent_id": "US12345678",
  "title": "Novel Therapeutic Compound",
  "abstract": "A method for treating...",
  "expiration_date": "2024-12-31T00:00:00",
  "grant_date": "2004-12-31T00:00:00",
  "inventor": "Smith, John",
  "assignee": "Pharma Corp",
  "technology_area": "biotechnology",
  "summary": "AI-generated summary...",
  "relevance_score": 0.95
}
```

### Get Usage Statistics

```http
GET /api/v1/stats
```

Get usage statistics for your API key.

**Response:**
```json
{
  "period": "last_30_days",
  "total_queries": 1500,
  "total_cost": 750.00,
  "average_response_time_ms": 245.5,
  "endpoints": [
    {
      "endpoint": "/api/v1/expirations",
      "count": 1200
    }
  ],
  "daily_usage": [
    {
      "date": "2024-01-01",
      "count": 50
    }
  ],
  "rate_limits": {
    "per_minute": 60,
    "per_day": 10000
  }
}
```

### Webhook Management

#### Create Webhook

```http
POST /api/v1/webhooks
```

Register a webhook endpoint for real-time alerts.

**Request Body:**
```json
{
  "url": "https://your-platform.com/webhooks/patents",
  "secret": "optional_webhook_secret",
  "events": ["patent.expired"]
}
```

**Response:**
```json
{
  "id": "webhook_id",
  "url": "https://your-platform.com/webhooks/patents",
  "is_active": true,
  "events": ["patent.expired"],
  "created_at": "2024-01-01T00:00:00"
}
```

#### List Webhooks

```http
GET /api/v1/webhooks
```

Get all registered webhooks for your API key.

#### Delete Webhook

```http
DELETE /api/v1/webhooks/{webhook_id}
```

Delete a webhook registration.

### API Key Management

#### Create API Key

```http
POST /api/v1/auth/keys
```

Create a new API key (admin only).

**Request Body:**
```json
{
  "partner_name": "Example Corp",
  "partner_email": "contact@example.com",
  "rate_limit_per_minute": 60,
  "rate_limit_per_day": 10000,
  "branding_enabled": true,
  "expires_in_days": 365
}
```

#### Get Current API Key

```http
GET /api/v1/auth/keys/me
```

Get information about your current API key.

#### Revoke API Key

```http
POST /api/v1/auth/keys/{key_id}/revoke
```

Revoke an API key (admin only).

## Webhook Events

### Patent Expired

Sent when a patent expires.

**Payload:**
```json
{
  "event": "patent.expired",
  "timestamp": "2024-01-01T00:00:00",
  "data": {
    "patent_id": "US12345678",
    "title": "Novel Therapeutic Compound",
    "expiration_date": "2024-01-01T00:00:00",
    ...
  }
}
```

**Headers:**
- `X-Webhook-Signature`: HMAC SHA256 signature (if secret configured)

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid query parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or inactive API key"
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error fetching patent data"
}
```

## Industry Keywords

Supported industry values:
- `biotech` - Biotechnology and pharmaceuticals
- `electronics` - Electronics and semiconductors
- `software` - Software and algorithms
- `medical` - Medical devices
- `automotive` - Automotive technology
- `energy` - Energy and renewable resources
- `materials` - Materials science

## Best Practices

1. **Caching**: Results are cached for 1 hour. Implement client-side caching for frequently accessed data.
2. **Pagination**: Use `limit` and `offset` for large result sets.
3. **Error Handling**: Implement exponential backoff for retries.
4. **Webhooks**: Use webhooks for real-time updates instead of polling.
5. **Rate Limits**: Monitor rate limit headers and adjust request frequency accordingly.

## Support

For API support, contact: youssofsallam25@gmail.com

