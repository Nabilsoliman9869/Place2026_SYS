FROM python:3.10-slim-bullseye

# Install system dependencies (ODBC Driver for SQL Server)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    ca-certificates \
    unixodbc-dev \
    g++ \
    apt-transport-https \
    && rm -rf /var/lib/apt/lists/*

# Add SQL Server ODBC Driver 17 (Compatible with most legacy servers)
RUN curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

# Fix SSL error for legacy SQL Servers (Allow TLS 1.0/1.1)
# This is CRITICAL for connecting to older SQL Servers like the one used in Place2026
RUN sed -i 's/MinProtocol = TLSv1.2/MinProtocol = TLSv1.0/' /etc/ssl/openssl.cnf \
    && sed -i 's/CipherString = DEFAULT@SECLEVEL=2/CipherString = DEFAULT@SECLEVEL=1/' /etc/ssl/openssl.cnf

# Set work directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render sets $PORT env var, but we expose standard 8000 for local testing)
EXPOSE 8000

# Run command
# Gunicorn is used for production Flask deployment
# binds to 0.0.0.0 and the PORT environment variable provided by Render
CMD gunicorn app:app --bind 0.0.0.0:$PORT
