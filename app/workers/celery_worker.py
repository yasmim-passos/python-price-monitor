from celery import Celery
from celery.schedules import crontab
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.cache import redis_client
from app.services.monitor import PriceMonitorService
import asyncio

# Initialize Celery
celery_app = Celery(
    "price_monitor_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    "check-all-products-hourly": {
        "task": "app.workers.celery_worker.check_all_products_task",
        "schedule": crontab(minute=0),  # Every hour
    },
}


@celery_app.task(name="app.workers.celery_worker.check_product_task")
def check_product_task(product_id: int):
    """Background task to check a single product price"""
    db = SessionLocal()
    try:
        monitor = PriceMonitorService(db, redis_client)
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(monitor.check_product_price(product_id))
        loop.close()
        
        return {
            "status": "success",
            "product_id": product_id,
            "result": result
        }
    except Exception as e:
        return {
            "status": "error",
            "product_id": product_id,
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.workers.celery_worker.check_all_products_task")
def check_all_products_task():
    """Background task to check all active products"""
    db = SessionLocal()
    try:
        monitor = PriceMonitorService(db, redis_client)
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(monitor.check_all_products())
        loop.close()
        
        return {
            "status": "success",
            "checked_count": len(results),
            "results": results
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="app.workers.celery_worker.cleanup_old_history_task")
def cleanup_old_history_task(days: int = 90):
    """Clean up price history older than specified days"""
    from datetime import datetime, timedelta
    from app.domain import PriceHistory
    
    db = SessionLocal()
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted_count = db.query(PriceHistory).filter(
            PriceHistory.timestamp < cutoff_date
        ).delete()
        
        db.commit()
        
        return {
            "status": "success",
            "deleted_count": deleted_count
        }
    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()
