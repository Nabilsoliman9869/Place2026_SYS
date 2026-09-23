FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ACCEPT_EULA=Y \
    DEBIAN_FRONTEND=noninteractive

# Debian 11 (bullseye) LTS ended 31 Aug 2026 — apt-get update fails on Railway.
# Debian 12 (bookworm) is supported until June 2028.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    ca-certificates \
    unixodbc \
    unixodbc-dev \
    g++ \
    apt-transport-https \
    libgssapi-krb5-2 \
    && rm -rf /var/lib/apt/lists/*

# Microsoft ODBC: prefer 17 (matches app connection strings), fall back to 18
RUN curl -sSL -O https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm -f packages-microsoft-prod.deb \
    && apt-get update \
    && (ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 \
        || ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18) \
    && rm -rf /var/lib/apt/lists/*

# Legacy SQL Server at xtra.webhop.me still needs TLS 1.0/1.1
RUN if [ -f /etc/ssl/openssl.cnf ]; then \
      sed -i 's/MinProtocol = TLSv1.2/MinProtocol = TLSv1.0/g' /etc/ssl/openssl.cnf \
      && sed -i 's/CipherString = DEFAULT@SECLEVEL=2/CipherString = DEFAULT@SECLEVEL=1/g' /etc/ssl/openssl.cnf; \
    fi

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD gunicorn app:app --config gunicorn.conf.py
