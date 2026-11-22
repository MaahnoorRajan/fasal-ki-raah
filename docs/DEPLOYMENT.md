# Deploy the Fasal Ki Raah demonstration

The release includes a WSGI application, pinned Waitress and WhiteNoise dependencies, a Docker recipe, a readiness endpoint and a versioned public-data import. A hosting account, HTTPS hostname and persistent volume are still needed.

## Build and run with Docker

Build from the repository root. Install Docker before running these commands.

```sh
docker build -t fasal-ki-raah .
docker volume create fasal-data
docker run -d --name fasal-ki-raah --restart unless-stopped --env-file /path/to/private.env -p 127.0.0.1:8000:8000 -v fasal-data:/data fasal-ki-raah
```

Use .env.example as a template for the private environment file. Generate a secret with Python's secrets.token_urlsafe(50) and keep it outside the repository. Set the real hostname and HTTPS origin. The entry point backs up an existing database, runs migrations, imports the bundled price snapshot and starts Waitress.

Configure an HTTPS reverse proxy to forward traffic to port 8000. WhiteNoise serves collected CSS and JavaScript through the application. Enable FASAL_TRUST_PROXY only if the proxy replaces incoming forwarded headers, and set FASAL_PROXY_IP to the proxy address seen inside the container. Waitress must trust that address to retain its protocol header. Keep the backend port private.

Attach /data to persistent storage on the host. The named Docker volume preserves accounts and bookings across container replacement. Use a single application instance with this SQLite configuration. A future multi-instance deployment requires a shared database and concurrency tests for that database.

## Without Docker

Create a Python 3.12 virtual environment and install requirements.txt. Set all environment variables from .env.example, using an absolute persistent database path. Run the following from the project root.

```sh
python tools/backup-database.py
python manage.py migrate --noinput
python manage.py import_market_prices
python manage.py collectstatic --noinput
python manage.py check --deploy --fail-level ERROR
waitress-serve --listen=127.0.0.1:8000 --threads=4 --trusted-proxy=127.0.0.1 --trusted-proxy-headers=x-forwarded-proto fasal.wsgi:application
```

The deployment check reports optional HSTS subdomain and preload warnings. Decide those settings after confirming HTTPS coverage for the hosting domain and its subdomains.

## Verify and maintain

- Configure the hosting readiness check to GET /health/. It returns 200 after the database and imported price table are available, or 503 if unavailable.
- Verify HTTPS login, price filters, static assets and a complete booking workflow with two fictional accounts.
- Recreate the container using the same volume and confirm those records survive.
- Startup backups are in the database directory's backups folder. Copy backups to private offsite storage, define a retention period and test restoring a backup into a separate database.
- Retain application logs and configure error alerts through the hosting provider.
- The source build was tested with Waitress in deployment mode. Docker image building requires a Docker engine and must be checked on the deployment machine.

## Scope of the first hosted release

This release supports a demonstration with fictional journeys and historical public price references. Account recovery, driver/phone verification, abuse controls and a support process for missed pickups or damaged cargo remain pilot work. Delivery is confirmed by the sender after checking with their recipient. Loading, unloading and payment are arranged directly.

References include the [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/) and [WhiteNoise configuration](https://whitenoise.readthedocs.io/en/stable/django.html).
