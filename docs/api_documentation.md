# Hello World API Documentation

## Overview

This document provides detailed information about the Hello World API, including endpoints, request/response formats, error handling, authentication (if implemented in the future), and usage examples.

## Base URL

Development: `http://localhost:8000`
Production: `https://api.yourdomain.com` (Replace with your actual domain)

## API Versioning

The API supports versioning via URL path. The current version is `v1`.

- Version 1: `/api/v1/`

## Common Headers

| Header Name | Description |
|-------------|-------------|
| Content-Type | Application/json for most endpoints |
| Authorization | For future authentication implementation |

## Rate Limiting

The API implements rate limiting to prevent abuse. Current limits:

- General rate limit: 100 requests per minute per IP address

When a rate limit is exceeded, the API returns a `429 Too Many Requests` status code.

## Endpoints

### Root Endpoint

Returns a simple "Hello World" message.

#### Request

```
GET /api/v1/
```

#### Response

```json
{
  "message": "Hello world!"
}
```

#### Status Codes

- 200: Success
- 429: Rate limit exceeded
- 500: Internal server error

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/"
```

### Health Check Endpoint

Returns detailed information about the service health and status.

#### Request

```
GET /api/v1/health
```

#### Response

```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "uptime_human": "1h 0m 0s",
  "system": {
    "process_id": 1234,
    "hostname": "api-server",
    "cpu_usage": 5.2,
    "memory_usage": 25.7,
    "disk_usage": 42.3
  }
}
```

#### Status Codes

- 200: Success
- 429: Rate limit exceeded
- 500: Internal server error

#### Example

```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

## Error Handling

The API uses standard HTTP status codes and returns detailed error messages in a consistent format:

```json
{
  "detail": "Error description"
}
```

### Common Error Codes

- 400: Bad Request - The request was invalid
- 401: Unauthorized - Authentication is required
- 403: Forbidden - The user does not have permission
- 404: Not Found - The requested resource does not exist
- 429: Too Many Requests - Rate limit exceeded
- 500: Internal Server Error - An unexpected error occurred

## Future Authentication

When authentication is implemented, the API will use OAuth2 with JWT tokens. The following is a placeholder for future implementation:

```
POST /api/v1/auth/token

Request Body:
{
  "username": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Development Guides

### Local Development

1. Clone the repository
2. Install dependencies with Poetry: `poetry install`
3. Run the development server: `poetry run python run.py`
4. Access the API at http://localhost:8000

### Testing Endpoints

You can test the API using curl, Postman, or any HTTP client:

```bash
# Test root endpoint
curl -X GET "http://localhost:8000/api/v1/"

# Test health endpoint
curl -X GET "http://localhost:8000/api/v1/health"
```

## Changelog

### v1.0.0 (Latest)

- Initial API release
- Implemented root and health endpoints
- Added rate limiting
- Set up security headers 