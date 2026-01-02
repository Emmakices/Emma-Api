FROM python:3.12-slim

# -------------------------------------------------
# Install system dependencies
# -------------------------------------------------
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gpg \
    apt-transport-https \
    ca-certificates \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------------
# Install Microsoft ODBC Driver 18 for SQL Server
# -------------------------------------------------
RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
    | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg \
    && chmod 644 /etc/apt/keyrings/microsoft.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/microsoft-prod.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------------
# Set working directory
# -------------------------------------------------
WORKDIR /app

# -------------------------------------------------
# Install Python dependencies
# -------------------------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------------------------------
# Copy application code
# -------------------------------------------------
COPY . .

# -------------------------------------------------
# Expose API port
# -------------------------------------------------
EXPOSE 8000

# -------------------------------------------------
# Run FastAPI
# -------------------------------------------------
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]