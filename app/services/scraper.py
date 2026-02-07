import httpx
import re
from typing import Optional, Dict
from bs4 import BeautifulSoup
from datetime import datetime
from app.core.config import settings


class ScraperService:
    """Base scraper service for extracting product prices"""
    
    def __init__(self):
        self.timeout = settings.REQUEST_TIMEOUT
        self.max_retries = settings.MAX_RETRIES
    
    async def scrape_price(self, url: str) -> Optional[Dict]:
        """
        Scrape price from product URL
        Returns dict with price, title, and timestamp
        """
        try:
            # Determine scraper based on URL
            if "mercadolivre.com" in url or "mercadolibre.com" in url:
                return await self._scrape_mercadolivre(url)
            elif "amazon.com" in url or "amazon.com.br" in url:
                return await self._scrape_amazon(url)
            else:
                return await self._scrape_generic(url)
        
        except Exception as e:
            print(f"Scraping error for {url}: {e}")
            return None
    
    async def _scrape_mercadolivre(self, url: str) -> Optional[Dict]:
        """Scrape Mercado Livre products"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(url, headers=headers, follow_redirects=True)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, "lxml")
                    
                    # Try multiple selectors for price
                    price_elem = (
                        soup.find("span", class_="andes-money-amount__fraction") or
                        soup.find("span", {"class": re.compile("price.*fraction")}) or
                        soup.find("meta", {"property": "og:price:amount"})
                    )
                    
                    if not price_elem:
                        continue
                    
                    # Extract price
                    if price_elem.name == "meta":
                        price_text = price_elem.get("content", "")
                    else:
                        price_text = price_elem.get_text(strip=True)
                    
                    # Clean and convert price
                    price_text = re.sub(r'[^\d,.]', '', price_text)
                    price_text = price_text.replace(',', '.')
                    price = float(price_text)
                    
                    # Get title
                    title_elem = soup.find("h1", class_="ui-pdp-title") or soup.find("h1")
                    title = title_elem.get_text(strip=True) if title_elem else "Product"
                    
                    return {
                        "price": price,
                        "title": title,
                        "timestamp": datetime.utcnow(),
                        "source": "Mercado Livre"
                    }
                
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise
                    continue
        
        return None
    
    async def _scrape_amazon(self, url: str) -> Optional[Dict]:
        """Scrape Amazon products"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
            }
            
            for attempt in range(self.max_retries):
                try:
                    response = await client.get(url, headers=headers, follow_redirects=True)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.text, "lxml")
                    
                    # Try multiple selectors for price
                    price_elem = (
                        soup.find("span", class_="a-price-whole") or
                        soup.find("span", id="priceblock_ourprice") or
                        soup.find("span", id="priceblock_dealprice")
                    )
                    
                    if not price_elem:
                        continue
                    
                    price_text = price_elem.get_text(strip=True)
                    price_text = re.sub(r'[^\d,.]', '', price_text)
                    price_text = price_text.replace(',', '.')
                    price = float(price_text)
                    
                    # Get title
                    title_elem = soup.find("span", id="productTitle")
                    title = title_elem.get_text(strip=True) if title_elem else "Product"
                    
                    return {
                        "price": price,
                        "title": title,
                        "timestamp": datetime.utcnow(),
                        "source": "Amazon"
                    }
                
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        raise
                    continue
        
        return None
    
    async def _scrape_generic(self, url: str) -> Optional[Dict]:
        """Generic scraper for other sites"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            try:
                response = await client.get(url, headers=headers, follow_redirects=True)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, "lxml")
                
                # Try common price patterns
                price_patterns = [
                    r'R\$\s*[\d.,]+',
                    r'BRL\s*[\d.,]+',
                    r'[\d.,]+',
                ]
                
                text = soup.get_text()
                for pattern in price_patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        price_text = matches[0]
                        price_text = re.sub(r'[^\d,.]', '', price_text)
                        price_text = price_text.replace(',', '.')
                        
                        try:
                            price = float(price_text)
                            if 0 < price < 1000000:  # Sanity check
                                title_elem = soup.find("h1") or soup.find("title")
                                title = title_elem.get_text(strip=True) if title_elem else "Product"
                                
                                return {
                                    "price": price,
                                    "title": title,
                                    "timestamp": datetime.utcnow(),
                                    "source": "Generic"
                                }
                        except ValueError:
                            continue
            
            except Exception as e:
                print(f"Generic scraper error: {e}")
        
        return None


# Singleton instance
scraper_service = ScraperService()
