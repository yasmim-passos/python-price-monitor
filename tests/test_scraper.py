import pytest
from unittest.mock import patch, AsyncMock
from app.services.scraper import ScraperService


class TestScraperService:
    """Tests for scraping service"""
    
    @pytest.fixture
    def scraper(self):
        return ScraperService()
    
    @pytest.mark.asyncio
    async def test_scrape_price_mock_mercadolivre(self, scraper):
        """Test scraping Mercado Livre (mocked)"""
        mock_html = """
        <html>
            <span class="andes-money-amount__fraction">1999</span>
            <h1 class="ui-pdp-title">iPhone 15 Pro</h1>
        </html>
        """
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.text = mock_html
            mock_response.raise_for_status = AsyncMock()
            mock_get.return_value = mock_response
            
            result = await scraper._scrape_mercadolivre(
                "https://www.mercadolivre.com.br/product"
            )
            
            assert result is not None
            assert result["price"] == 1999.0
            assert "iPhone" in result["title"]
            assert result["source"] == "Mercado Livre"
    
    @pytest.mark.asyncio
    async def test_scrape_price_invalid_url(self, scraper):
        """Test scraping with connection error"""
        with patch("httpx.AsyncClient.get", side_effect=Exception("Connection error")):
            result = await scraper.scrape_price("https://invalid-url.com/product")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_scrape_generic_fallback(self, scraper):
        """Test generic scraper fallback"""
        mock_html = """
        <html>
            <h1>Test Product</h1>
            <div>Price: R$ 150,50</div>
        </html>
        """
        
        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = AsyncMock()
            mock_response.text = mock_html
            mock_response.raise_for_status = AsyncMock()
            mock_get.return_value = mock_response
            
            result = await scraper._scrape_generic("https://example.com/product")
            
            assert result is not None
            assert result["price"] == 150.50
            assert "Test Product" in result["title"]
