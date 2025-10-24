"""Background scheduler with Redis lock for policy expiry logging."""
from __future__ import annotations
from datetime import date, datetime
from zoneinfo import ZoneInfo
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
import structlog

from core.settings import settings
from core.logging import get_logger
from core.redis import acquire_lock, release_lock
from db.session import get_db
from services.policy_service import (
    get_unlogged_expiring_policies,
    mark_policy_logged,
)

log = get_logger()

LOCK_KEY = settings.REDIS_LOCK_KEY
LOCK_TTL_SECONDS = settings.REDIS_LOCK_TTL_SECONDS  # Prevent overlapping runs within a minute


def _run_policy_expiry_job():
    if not acquire_lock(LOCK_KEY, LOCK_TTL_SECONDS):
        # Another instance is running the job
        return
    # Use dependency function to get a session
    session_generator = get_db()
    db: Session = next(session_generator)
    try:
        tz = ZoneInfo(settings.SCHEDULER_TIMEZONE)
        now_local = datetime.now(tz)
        # First hour window start inclusive, end exclusive
        start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(hour=1)
        in_window = start <= now_local < end
        today = now_local.date()

        # Fallback: if we are outside the window but nothing has been logged yet for today
        # (e.g., scheduler started late), allow a single catch-up run.
        expiring = get_unlogged_expiring_policies(db, today)
        if not expiring:
            return
        if not in_window:
            # Check if any policy already has logged_expiry_at today (catch-up logic)
            # If any are logged, skip; else proceed.
            already_logged = any(p.logged_expiry_at and p.logged_expiry_at.date() == today for p in expiring)
            if already_logged:
                return
            log.info("policy_expiry_catchup", date=today.isoformat())
        for p in expiring:
            log.info(
                "policy_expiry_logged",
                policyId=p.id,
                carId=p.car_id,
                endDate=p.end_date.isoformat(),
                inWindow=in_window,
            )
            mark_policy_logged(db, p, now_local)
        db.commit()
    except Exception:
        log.exception("policy_expiry_job_error")
    finally:
        db.close()
        release_lock(LOCK_KEY)


_scheduler: BackgroundScheduler | None = None


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    if not settings.SCHEDULER_ENABLED:
        log.info("scheduler_disabled")
        return
    _scheduler = BackgroundScheduler(timezone=settings.SCHEDULER_TIMEZONE)
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
