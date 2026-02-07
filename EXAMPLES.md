# Exemplos de Uso da API - Price Monitor

## Usando cURL

### 1. Registrar e fazer login

```bash
# Registrar novo usuário
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "maria@example.com",
    "username": "maria",
    "password": "senha123"
  }'

# Fazer login e salvar token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=maria&password=senha123" | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 2. Gerenciar produtos

```bash
# Adicionar produto do Mercado Livre
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Notebook Dell",
    "url": "https://www.mercadolivre.com.br/notebook-dell"
  }'

# Listar todos os produtos
curl -X GET "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer $TOKEN"

# Ver detalhes de um produto específico
curl -X GET "http://localhost:8000/api/v1/products/1" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Configurar alertas

```bash
# Criar alerta para quando preço cair abaixo de R$ 2000
curl -X POST "http://localhost:8000/api/v1/alerts/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "target_price": 2000.00
  }'

# Listar alertas ativos
curl -X GET "http://localhost:8000/api/v1/alerts/?active_only=true" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Monitorar preços

```bash
# Verificar preço manualmente
curl -X POST "http://localhost:8000/api/v1/monitor/check/1" \
  -H "Authorization: Bearer $TOKEN"

# Verificar todos os produtos
curl -X POST "http://localhost:8000/api/v1/monitor/check-all" \
  -H "Authorization: Bearer $TOKEN"

# Ver estatísticas de preço
curl -X GET "http://localhost:8000/api/v1/monitor/stats/1" \
  -H "Authorization: Bearer $TOKEN"

# Ver histórico de preços
curl -X GET "http://localhost:8000/api/v1/products/1/history" \
  -H "Authorization: Bearer $TOKEN"
```

## Usando Python (requests)

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 1. Registrar usuário
register_data = {
    "email": "joao@example.com",
    "username": "joao",
    "password": "senha123"
}
response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
print("Usuário criado:", response.json())

# 2. Fazer login
login_data = {
    "username": "joao",
    "password": "senha123"
}
response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 3. Adicionar produto
product_data = {
    "name": "iPhone 15 Pro",
    "url": "https://www.mercadolivre.com.br/iphone-15-pro"
}
response = requests.post(f"{BASE_URL}/products/", json=product_data, headers=headers)
product = response.json()
print("Produto criado:", product)

# 4. Criar alerta
alert_data = {
    "product_id": product["id"],
    "target_price": 6500.00
}
response = requests.post(f"{BASE_URL}/alerts/", json=alert_data, headers=headers)
print("Alerta criado:", response.json())

# 5. Verificar preço
response = requests.post(
    f"{BASE_URL}/monitor/check/{product['id']}", 
    headers=headers
)
print("Preço atual:", response.json())

# 6. Ver estatísticas
response = requests.get(
    f"{BASE_URL}/monitor/stats/{product['id']}", 
    headers=headers
)
print("Estatísticas:", response.json())
```

## Usando JavaScript (fetch)

```javascript
const BASE_URL = 'http://localhost:8000/api/v1';

// 1. Registrar usuário
async function registerUser() {
  const response = await fetch(`${BASE_URL}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'ana@example.com',
      username: 'ana',
      password: 'senha123'
    })
  });
  return response.json();
}

// 2. Fazer login
async function login() {
  const formData = new URLSearchParams();
  formData.append('username', 'ana');
  formData.append('password', 'senha123');
  
  const response = await fetch(`${BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData
  });
  
  const data = await response.json();
  return data.access_token;
}

// 3. Adicionar produto
async function addProduct(token) {
  const response = await fetch(`${BASE_URL}/products/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      name: 'MacBook Air',
      url: 'https://www.mercadolivre.com.br/macbook-air'
    })
  });
  return response.json();
}

// 4. Verificar preço
async function checkPrice(token, productId) {
  const response = await fetch(`${BASE_URL}/monitor/check/${productId}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
}

// Uso
(async () => {
  await registerUser();
  const token = await login();
  const product = await addProduct(token);
  const priceData = await checkPrice(token, product.id);
  console.log('Preço atual:', priceData);
})();
```

## Testando com Postman/Insomnia

1. Importe a coleção de endpoints disponível em `http://localhost:8000/docs`
2. Configure a variável de ambiente `token` após fazer login
3. Use `{{token}}` nos headers de Authorization

## Automação com Scripts

### Script para verificar preços diariamente

```bash
#!/bin/bash

# Script: check_prices.sh
TOKEN="seu-token-aqui"

echo "Verificando preços..."
curl -X POST "http://localhost:8000/api/v1/monitor/check-all" \
  -H "Authorization: Bearer $TOKEN" \
  -s | jq '.results[] | "\(.product_name): R$ \(.price)"'
```

### Cronjob para monitoramento automático

```bash
# Adicione ao crontab (crontab -e)
# Executa todo dia às 9h
0 9 * * * /path/to/check_prices.sh
```

## Dicas de Uso

1. **Salve o token**: Tokens expiram em 30 minutos. Salve e renove quando necessário.

2. **Use filtros**: Endpoints de listagem suportam `skip` e `limit` para paginação.

3. **Monitore com Flower**: Acesse http://localhost:5555 para ver tarefas em execução.

4. **Veja os logs**: `docker-compose logs -f api` para debugar problemas.

5. **Rate limiting**: Respeite os limites de requisições para evitar bloqueios.
