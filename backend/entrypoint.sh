#!/bin/sh
set -e

PORT="${PORT:-9200}"

echo "Waiting for MySQL..."
python - <<'PY'
import os, time
from sqlalchemy import create_engine, text
from app.config import settings

url = settings.database_url
for i in range(60):
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database is ready.")
        break
    except Exception as e:
        print(f"DB not ready ({i+1}/60): {e}")
        time.sleep(2)
else:
    raise SystemExit("Database not ready after retries")
PY

echo "Creating tables..."
python -c "from app.database import Base, engine; from app import models; Base.metadata.create_all(bind=engine)"

echo "Normalizing mill statuses..."
python - <<'PY'
from sqlalchemy import text
from app.database import engine

with engine.begin() as conn:
    # 存量脏数据（大小写/空白差异）收敛到约定枚举；无法识别的回落到 idle。
    rows = conn.execute(text("SELECT id, status FROM mills")).fetchall()
    for row_id, raw in rows:
        status = (raw or "").strip().lower()
        if status not in ("grinding", "idle", "wash"):
            status = "idle"
        if status != raw:
            conn.execute(text("UPDATE mills SET status = :s WHERE id = :id"), {"s": status, "id": row_id})
PY

if [ "${SEED_ON_START}" = "true" ] || [ "${SEED_ON_START}" = "1" ]; then
  echo "Seeding data..."
  python -c "from app.seed import seed; seed()"
fi

echo "Starting gunicorn on :${PORT}..."
exec gunicorn wsgi:app --bind "0.0.0.0:${PORT}" --workers 2 --threads 4 --timeout 120
