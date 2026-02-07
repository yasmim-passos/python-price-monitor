from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.core.cache import get_redis
from app.domain import User, Product
from app.services.monitor import PriceMonitorService

router = APIRouter(prefix="/monitor", tags=["Monitoring"])


@router.post("/check/{product_id}")
async def check_product_price(
    product_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    cache = Depends(get_redis)
):
    """Manually trigger price check for a specific product"""
    # Verify product belongs to user
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    monitor = PriceMonitorService(db, cache)
    result = await monitor.check_product_price(product_id)
    
    if not result:
        raise HTTPException(
            status_code=500,
            detail="Failed to scrape product price. Check if URL is valid."
        )
    
    return {
        "product_id": product_id,
        "product_name": product.name,
        "scraped_data": result
    }


@router.post("/check-all")
async def check_all_user_products(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    cache = Depends(get_redis)
):
    """Check prices for all user's products"""
    monitor = PriceMonitorService(db, cache)
    results = await monitor.check_all_products(user_id=current_user.id)
    
    return {
        "checked_count": len(results),
        "results": results
    }


@router.get("/stats/{product_id}")
async def get_product_stats(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    cache = Depends(get_redis)
):
    """Get price statistics for a product"""
    # Verify product belongs to user
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    monitor = PriceMonitorService(db, cache)
    stats = monitor.get_price_stats(product_id)
    
    if not stats:
        raise HTTPException(
            status_code=404,
            detail="No price history available for this product"
        )
    
    return stats
