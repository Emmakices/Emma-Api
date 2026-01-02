import os
import urllib.parse
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, Query, Header, HTTPException, Depends, Request
from sqlalchemy import create_engine, text

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# -------------------------------------------------
# Load environment variables
# -------------------------------------------------
load_dotenv()

# -------------------------------------------------
# FastAPI app
# -------------------------------------------------
app = FastAPI(title="Ecom Events API")

# -------------------------------------------------
# Rate Limiter Setup
# -------------------------------------------------
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# -------------------------------------------------
# Database Connection
# -------------------------------------------------
def build_conn_str():
    odbc = (
        f"DRIVER={{{os.getenv('SQLSERVER_DRIVER')}}};"
        f"SERVER={os.getenv('SQLSERVER_HOST')},{os.getenv('SQLSERVER_PORT')};"
        f"DATABASE={os.getenv('SQLSERVER_DB')};"
        f"UID={os.getenv('SQLSERVER_USER')};"
        f"PWD={os.getenv('SQLSERVER_PASSWORD')};"
        "TrustServerCertificate=yes;"
    )
    return "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(odbc)

engine = create_engine(build_conn_str(), pool_pre_ping=True)

# -------------------------------------------------
# API Key Security
# -------------------------------------------------
def require_api_key(x_api_key: str = Header(None, alias="X-API-KEY")):
    expected = os.getenv("API_KEY")
    if not expected or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

# -------------------------------------------------
# Public Health Endpoint
# -------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------------------------------
# Protected Dataset Endpoint
# -------------------------------------------------
@app.get("/datasets/ecom_events", dependencies=[Depends(require_api_key)])
@limiter.limit("30/minute")
def get_ecom_events(
    request: Request,  # REQUIRED for SlowAPI
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    start_time: datetime | None = Query(
        None, description="ISO datetime e.g. 2019-10-01T00:00:00"
    ),
    end_time: datetime | None = Query(
        None, description="ISO datetime e.g. 2019-11-01T00:00:00"
    ),
):
    # Enforce correct date filtering
    if (start_time and not end_time) or (end_time and not start_time):
        raise HTTPException(
            status_code=400,
            detail="Provide both start_time and end_time",
        )

    offset = (page - 1) * page_size
    where_clause = ""
    params = {"offset": offset, "limit": page_size}

    if start_time and end_time:
        where_clause = "WHERE event_time >= :start_time AND event_time < :end_time"
        params.update({"start_time": start_time, "end_time": end_time})

    count_query = text(
        f"SELECT COUNT(1) AS total FROM api.v_ecom_events {where_clause}"
    )

    data_query = text(
        f"""
        SELECT *
        FROM api.v_ecom_events
        {where_clause}
        ORDER BY event_time
        OFFSET :offset ROWS
        FETCH NEXT :limit ROWS ONLY
        """
    )

    with engine.connect() as conn:
        total = conn.execute(count_query, params).scalar()
        rows = conn.execute(data_query, params).mappings().all()

    return {
        "dataset": "ecom_events",
        "meta": {"page": page, "page_size": page_size, "total": total},
        "data": [dict(r) for r in rows],
    }
