# 📖 API Endpoints Guide

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

### Register User
**POST** `/auth/register`

Request:
```json
{
  "email": "user@example.com",
  "username": "myuser",
  "password": "securepass123"
}
```

Response (201):
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "myuser",
  "is_active": true,
  "created_at": "2024-01-20T10:30:00"
}
```

### Login
**POST** `/auth/login`

Request (form-data):
```
username=myuser
password=securepass123
```

Response (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Products

### Create Product
**POST** `/products/`

Headers: `Authorization: Bearer {token}`

Request:
```json
{
  "name": "iPhone 15 Pro",
  "url": "https://www.mercadolivre.com.br/produto"
}
```

Response (201):
```json
{
  "id": 1,
  "user_id": 1,
  "name": "iPhone 15 Pro",
  "url": "https://www.mercadolivre.com.br/produto",
  "current_price": null,
  "last_checked": null,
  "is_active": true,
  "created_at": "2024-01-20T10:35:00"
}
```

### List Products
**GET** `/products/?skip=0&limit=100`

Headers: `Authorization: Bearer {token}`

Response (200):
```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "iPhone 15 Pro",
    "url": "https://www.mercadolivre.com.br/produto",
    "current_price": 7999.99,
    "last_checked": "2024-01-20T11:00:00",
    "is_active": true,
    "created_at": "2024-01-20T10:35:00"
  }
]
```

### Get Product
**GET** `/products/{product_id}`

Headers: `Authorization: Bearer {token}`

Response (200): Same as product object

### Update Product
**PATCH** `/products/{product_id}`

Headers: `Authorization: Bearer {token}`

Request:
```json
{
  "name": "iPhone 15 Pro Max",
  "is_active": true
}
```

Response (200): Updated product object

### Delete Product
**DELETE** `/products/{product_id}`

Headers: `Authorization: Bearer {token}`

Response (204): No content

### Get Price History
**GET** `/products/{product_id}/history?skip=0&limit=100`

Headers: `Authorization: Bearer {token}`

Response (200):
```json
[
  {
    "id": 1,
    "product_id": 1,
    "price": 7999.99,
    "timestamp": "2024-01-20T11:00:00"
  },
  {
    "id": 2,
    "product_id": 1,
    "price": 7899.99,
    "timestamp": "2024-01-20T10:00:00"
  }
]
```

## Alerts

### Create Alert
**POST** `/alerts/`

Headers: `Authorization: Bearer {token}`

Request:
```json
{
  "product_id": 1,
  "target_price": 6999.00
}
```

Response (201):
```json
{
  "id": 1,
  "user_id": 1,
  "product_id": 1,
  "target_price": 6999.00,
  "is_active": true,
  "triggered_at": null,
  "created_at": "2024-01-20T10:40:00"
}
```

### List Alerts
**GET** `/alerts/?skip=0&limit=100&active_only=true`

Headers: `Authorization: Bearer {token}`

Response (200):
```json
[
  {
    "id": 1,
    "user_id": 1,
    "product_id": 1,
    "target_price": 6999.00,
    "is_active": true,
    "triggered_at": null,
    "created_at": "2024-01-20T10:40:00"
  }
]
```

### Delete Alert
**DELETE** `/alerts/{alert_id}`

Headers: `Authorization: Bearer {token}`

Response (204): No content

## Monitoring

### Check Product Price
**POST** `/monitor/check/{product_id}`

Headers: `Authorization: Bearer {token}`

Response (200):
```json
{
  "product_id": 1,
  "product_name": "iPhone 15 Pro",
  "scraped_data": {
    "price": 7999.99,
    "title": "Apple iPhone 15 Pro 256GB",
    "timestamp": "2024-01-20T12:00:00",
    "source": "Mercado Livre"
  }
}
```

### Check All User Products
**POST** `/monitor/check-all`

Headers: `Authorization: Bearer {token}`

Response (200):
```json
{
  "checked_count": 3,
  "results": [
    {
      "product_id": 1,
      "product_name": "iPhone 15 Pro",
      "price": 7999.99,
      "title": "Apple iPhone 15 Pro 256GB",
      "timestamp": "2024-01-20T12:00:00",
      "source": "Mercado Livre"
    }
  ]
}
```

### Get Product Stats
**GET** `/monitor/stats/{product_id}`

Headers: `Authorization: Bearer {token}`

Response (200):
```json
{
  "product_id": 1,
  "current_price": 7999.99,
  "min_price": 7899.99,
  "max_price": 8199.99,
  "avg_price": 7999.99,
  "price_changes": 5,
  "last_checked": "2024-01-20T12:00:00"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Product not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## Rate Limiting

- Anonymous requests: 100/hour
- Authenticated requests: 1000/hour
- Scraping requests: 60/hour per user

## Notes

- All timestamps are in UTC
- Prices are stored as floats
- URLs must be valid HTTP/HTTPS links
- Authentication tokens expire after 30 minutes (configurable)
