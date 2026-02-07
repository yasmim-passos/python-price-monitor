import pytest
from fastapi import status


class TestAlerts:
    """Tests for price alert endpoints"""
    
    def test_create_alert(self, client, auth_headers, test_product):
        """Test creating a price alert"""
        response = client.post(
            "/api/v1/alerts/",
            headers=auth_headers,
            json={
                "product_id": test_product.id,
                "target_price": 79.99
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["product_id"] == test_product.id
        assert data["target_price"] == 79.99
        assert data["is_active"] is True
    
    def test_create_alert_nonexistent_product(self, client, auth_headers):
        """Test creating alert for non-existent product"""
        response = client.post(
            "/api/v1/alerts/",
            headers=auth_headers,
            json={
                "product_id": 99999,
                "target_price": 50.0
            }
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_alert_invalid_price(self, client, auth_headers, test_product):
        """Test creating alert with invalid price"""
        response = client.post(
            "/api/v1/alerts/",
            headers=auth_headers,
            json={
                "product_id": test_product.id,
                "target_price": -10.0  # Negative price
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_list_alerts(self, client, auth_headers, test_product, db_session):
        """Test listing alerts"""
        # Create an alert first
        client.post(
            "/api/v1/alerts/",
            headers=auth_headers,
            json={
                "product_id": test_product.id,
                "target_price": 79.99
            }
        )
        
        response = client.get("/api/v1/alerts/", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_list_alerts_active_only(self, client, auth_headers, test_product, db_session):
        """Test listing only active alerts"""
        response = client.get(
            "/api/v1/alerts/?active_only=true",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for alert in data:
            assert alert["is_active"] is True
    
    def test_delete_alert(self, client, auth_headers, test_product):
        """Test deleting an alert"""
        # Create alert
        create_response = client.post(
            "/api/v1/alerts/",
            headers=auth_headers,
            json={
                "product_id": test_product.id,
                "target_price": 79.99
            }
        )
        alert_id = create_response.json()["id"]
        
        # Delete alert
        response = client.delete(
            f"/api/v1/alerts/{alert_id}",
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    def test_delete_nonexistent_alert(self, client, auth_headers):
        """Test deleting non-existent alert"""
        response = client.delete("/api/v1/alerts/99999", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_create_alert_unauthorized(self, client, test_product):
        """Test creating alert without authentication"""
        response = client.post(
            "/api/v1/alerts/",
            json={
                "product_id": test_product.id,
                "target_price": 50.0
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
