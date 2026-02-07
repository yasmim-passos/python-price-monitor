from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.domain import Product, PriceHistory, PriceAlert
from app.services.scraper import scraper_service
from app.core.cache import RedisClient


class PriceMonitorService:
    """Service for monitoring product prices"""
    
    def __init__(self, db: Session, cache: RedisClient):
        self.db = db
        self.cache = cache
    
    async def check_product_price(self, product_id: int) -> Optional[dict]:
        """
        Check and update price for a specific product
        Returns the scraped data if successful
        """
        # Get product from database
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product or not product.is_active:
            return None
        
        # Check cache first
        cache_key = f"price:{product_id}"
        cached_price = self.cache.get(cache_key)
        if cached_price:
            return cached_price
        
        # Scrape price
        scraped_data = await scraper_service.scrape_price(product.url)
        if not scraped_data:
            return None
        
        # Update product
        product.current_price = scraped_data["price"]
        product.last_checked = datetime.utcnow()
        
        # Save to price history
        price_history = PriceHistory(
            product_id=product.id,
            price=scraped_data["price"],
            timestamp=datetime.utcnow()
        )
        self.db.add(price_history)
        
        # Check alerts
        await self._check_alerts(product)
        
        # Commit changes
        self.db.commit()
        
        # Cache the result
        self.cache.set(cache_key, scraped_data)
        
        return scraped_data
    
    async def check_all_products(self, user_id: Optional[int] = None) -> List[dict]:
        """
        Check prices for all active products
        Optionally filter by user_id
        """
        query = self.db.query(Product).filter(Product.is_active == True)
        
        if user_id:
            query = query.filter(Product.user_id == user_id)
        
        products = query.all()
        results = []
        
        for product in products:
            result = await self.check_product_price(product.id)
            if result:
                results.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    **result
                })
        
        return results
    
    async def _check_alerts(self, product: Product):
        """Check and trigger price alerts for a product"""
        if not product.current_price:
            return
        
        # Get active alerts for this product
        alerts = self.db.query(PriceAlert).filter(
            PriceAlert.product_id == product.id,
            PriceAlert.is_active == True
        ).all()
        
        for alert in alerts:
            if product.current_price <= alert.target_price:
                # Trigger alert
                alert.is_active = False
                alert.triggered_at = datetime.utcnow()
                
                # Here you could send email/notification
                print(f"🔔 ALERT TRIGGERED: Product {product.name} reached target price!")
                print(f"   Current: R$ {product.current_price:.2f}")
                print(f"   Target: R$ {alert.target_price:.2f}")
    
    def get_price_stats(self, product_id: int) -> Optional[dict]:
        """Get price statistics for a product"""
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        
        history = self.db.query(PriceHistory).filter(
            PriceHistory.product_id == product_id
        ).order_by(PriceHistory.timestamp.desc()).all()
        
        if not history:
            return None
        
        prices = [h.price for h in history]
        
        return {
            "product_id": product_id,
            "current_price": product.current_price,
            "min_price": min(prices),
            "max_price": max(prices),
            "avg_price": sum(prices) / len(prices),
            "price_changes": len(history),
            "last_checked": product.last_checked
        }
