# one-time fresh start (drops volume, recreates, migrates, seeds, runs api)
.\scripts\setup\db.ps1 -Init
.\scripts\setup\run.ps1 -Seed

# normal day-to-day (start everything, migrate, run api; no seeding)
.\scripts\setup\run.ps1

# only reseed (when API already running)
.\scripts\db\seed-database.ps1

# seeding with custom parameters (when API already running)
python scripts/seed.py --owners 10 --cars-per-owner 3 --policies-per-car 2 --claims-per-car 4 --purge

## Background Scheduler & Redis

The policy expiry logging job runs every `SCHEDULER_INTERVAL_MINUTES` (default 10) using APScheduler.
A Redis-backed lock ensures only one instance processes expiries when multiple API containers are running.

### Start Redis (local dev)

Option A – Docker:
```powershell
docker run --name redis -p 6379:6379 -d redis:7
```

Option B – Existing Redis:
Set environment variables in `.env`:
```
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### Verify Redis
Inside container:
```powershell
docker exec -it redis redis-cli PING
```

Python quick check:
```powershell
python - <<'PY'
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
print('PING response:', r.ping())
PY
```

### How the Job Works
1. Acquires Redis lock `policy-expiry-lock` (TTL 60s).
2. Queries policies with `end_date = today AND logged_expiry_at IS NULL`.
3. Logs each (`policy_expiry_logged`) and sets `logged_expiry_at`.
4. Releases lock.

### Adjust Interval
Set in `.env`:
```
SCHEDULER_INTERVAL_MINUTES=5
```

### Disabling Scheduler (optional)
Add to `.env` (if implemented later):
```
ENABLE_SCHEDULER=false
```

## Logging

Structured logging via structlog:
- Local/dev: human-readable console
- Other envs: JSON
- Override level: `LOG_LEVEL=DEBUG|INFO` (defaults DEBUG in local/dev, INFO elsewhere)

Emitted events:
| Event | When |
|-------|------|
| policy_created | Policy POST |
| policy_updated | Policy PUT |
| policy_deleted | Policy DELETE |
| claim_created  | Claim POST |
| claim_updated  | Claim PUT |
| claim_deleted  | Claim DELETE |
| policy_expiry_logged | Scheduler job expiry processing |

Each contains IDs (policyId, claimId, carId) and relevant attributes (provider, amount, endDate).