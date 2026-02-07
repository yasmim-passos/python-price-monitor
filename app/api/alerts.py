from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.domain import User, Product, PriceAlert
from app.domain.schemas import PriceAlertCreate, PriceAlertResponse

router = APIRouter(prefix="/alerts", tags=["Price Alerts"])


@router.post("/", response_model=PriceAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_data: PriceAlertCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a price alert"""
    # Verify product belongs to user
    product = db.query(Product).filter(
        Product.id == alert_data.product_id,
        Product.user_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    db_alert = PriceAlert(
        user_id=current_user.id,
        product_id=alert_data.product_id,
        target_price=alert_data.target_price
    )
    
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    
    return db_alert


@router.get("/", response_model=List[PriceAlertResponse])
async def list_alerts(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all alerts for current user"""
    query = db.query(PriceAlert).filter(PriceAlert.user_id == current_user.id)
    
    if active_only:
        query = query.filter(PriceAlert.is_active == True)
    
    alerts = query.offset(skip).limit(limit).all()
    return alerts


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a price alert"""
    alert = db.query(PriceAlert).filter(
        PriceAlert.id == alert_id,
        PriceAlert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    db.delete(alert)
    db.commit()
