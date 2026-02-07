import pytest
from fastapi import status


class TestProducts:
    """Tests for product endpoints"""
    
    def test_create_product(self, client, auth_headers):
        """Test creating a new product"""
        response = client.post(
            "/api/v1/products/",
            headers=auth_headers,
            json={
                "name": "iPhone 15",
                "url": "https://www.example.com/iphone15"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "iPhone 15"
        assert "id" in data
        assert data["is_active"] is True
    
    def test_create_product_unauthorized(self, client):
        """Test creating product without authentication"""
        response = client.post(
            "/api/v1/products/",
            json={
                "name": "Test Product",
                "url": "https://www.example.com/product"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_list_products(self, client, auth_headers, test_product):
        """Test listing user's products"""
        response = client.get("/api/v1/products/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["name"] == "Test Product"
    
    def test_get_product(self, client, auth_headers, test_product):
        """Test getting a specific product"""
        response = client.get(
            f"/api/v1/products/{test_product.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_product.id
        assert data["name"] == test_product.name
    
    def test_get_nonexistent_product(self, client, auth_headers):
        """Test getting non-existent product"""
        response = client.get("/api/v1/products/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_product(self, client, auth_headers, test_product):
        """Test updating a product"""
        response = client.patch(
            f"/api/v1/products/{test_product.id}",
            headers=auth_headers,
            json={"name": "Updated Product Name"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Product Name"
        assert data["id"] == test_product.id
    
    def test_update_product_deactivate(self, client, auth_headers, test_product):
        """Test deactivating a product"""
        response = client.patch(
            f"/api/v1/products/{test_product.id}",
            headers=auth_headers,
            json={"is_active": False}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["is_active"] is False
    
    def test_delete_product(self, client, auth_headers, test_product):
        """Test deleting a product"""
        response = client.delete(
            f"/api/v1/products/{test_product.id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's deleted
        response = client.get(
            f"/api/v1/products/{test_product.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_price_history_empty(self, client, auth_headers, test_product):
        """Test getting price history when empty"""
        response = client.get(
            f"/api/v1/products/{test_product.id}/history",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_product_invalid_url(self, client, auth_headers):
        """Test creating product with invalid URL"""
        response = client.post(
            "/api/v1/products/",
            headers=auth_headers,
            json={
                "name": "Test Product",
                "url": "not-a-valid-url"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
