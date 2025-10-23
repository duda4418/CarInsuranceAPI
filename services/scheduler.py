"""Background scheduler with Redis lock for policy expiry logging."""
from __future__ import annotations
from datetime import date, datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
import structlog

from core.settings import settings
from core.redis import acquire_lock, release_lock
from db.session import get_db
from services.policy_service import (
    get_unlogged_expiring_policies,
    mark_policy_logged,
)

log = structlog.get_logger()

LOCK_KEY = "policy-expiry-lock"
LOCK_TTL_SECONDS = 60  # Prevent overlapping runs within a minute


def _run_policy_expiry_job():
    if not acquire_lock(LOCK_KEY, LOCK_TTL_SECONDS):
        # Another instance is running the job
        return
    # Use dependency function to get a session
    session_generator = get_db()
    db: Session = next(session_generator)
    try:
        today = date.today()
        expiring = get_unlogged_expiring_policies(db, today)
        if not expiring:
            return
        now = datetime.utcnow()
        for p in expiring:
            log.info(
                "policy_expiry_logged",
                policyId=p.id,
                carId=p.car_id,
                endDate=p.end_date.isoformat(),
            )
            mark_policy_logged(db, p, now)
        db.commit()
    except Exception as e:
        log.error("policy_expiry_job_error", error=str(e))
    finally:
        db.close()
        release_lock(LOCK_KEY)


_scheduler: BackgroundScheduler | None = None


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(
        _run_policy_expiry_job,
        "interval",
        minutes=settings.SCHEDULER_INTERVAL_MINUTES,
        id="policy-expiry",
        max_instances=1,
        coalesce=True,
    )
    _scheduler.start()
    log.info("scheduler_started", intervalMinutes=settings.SCHEDULER_INTERVAL_MINUTES)


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        log.info("scheduler_stopped")
        _scheduler = None
