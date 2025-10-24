
# Car Insurance API - Quick Start

## 1. Clone the repository
```powershell
git clone <repo-url>
cd CarInsuranceAPI
```

## 2. Create and activate a virtual environment
```powershell
py -m venv .venv
.venv\Scripts\activate
```

## 3. Install dependencies
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Start PostgreSQL and Redis containers (Docker Compose)
```powershell
docker-compose up -d
```

## 5. Set environment variables
Copy `.env.example` to `.env` and update values if needed.

## 6. Run database migrations (if needed)
```powershell
alembic upgrade head
```

## 7. Start the application
```powershell
uvicorn main:app --reload
```

## 8. Run tests with coverage
```powershell
pytest --cov=. --cov-report=term-missing
```
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