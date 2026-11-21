# Host the Django demonstration

The app currently runs locally. These settings prepare a hosted demonstration with fictional accounts and shipments. A hosting account and public URL still need to be chosen.

## Configuration

Set environment variables through the host's settings panel or process environment. Django does not load a .env file automatically.

- FASAL_DEBUG=0 enables deployment mode.
- FASAL_SECRET_KEY must contain a persistent private random secret, at least 50 characters.
- FASAL_ALLOWED_HOSTS contains the exact hostname, such as demo.example.org.
- FASAL_CSRF_ORIGINS contains the HTTPS origin if needed, such as https://demo.example.org.
- FASAL_DATABASE_PATH points to a SQLite file on persistent storage outside the source checkout.
- FASAL_TRUST_PROXY=1 is appropriate only when a trusted HTTPS proxy removes incoming forwarded headers and supplies its own X-Forwarded-Proto header.

Deployment mode enables secure session and CSRF cookies, HTTPS redirects, content-type protection, frame protection and a one-hour HSTS policy. Development defaults remain suitable for the local launcher.

## Start on a Linux host

Install Python, the project requirements and Gunicorn in a virtual environment. Configure the environment above, then run from the project root.

```sh
python -m pip install -r requirements.txt gunicorn
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py check --deploy --fail-level ERROR
gunicorn fasal.wsgi:application --bind 127.0.0.1:8000 --workers 1
```

Configure the HTTPS reverse proxy to forward requests to port 8000 and serve /static/ from the generated staticfiles directory. Keep the backend port private. Configure the hosting service to restart the application after failures and send its output to retained logs.

The deployment check reports optional HSTS subdomain and preload warnings with these defaults. Enable those settings only after establishing HTTPS coverage for the relevant domain and subdomains.

SQLite supports the small demonstration using one persistent application instance. Test concurrency on the chosen host before allowing real bookings. A multi-instance deployment needs a shared database and corresponding migration and concurrency tests.

## Verify and recover

Create two fictional accounts through the public HTTPS URL. Test requesting, accepting, cancelling and completing separate bookings. Verify that the CSS loads and that unrelated accounts cannot read booking details.

Back up the database before every schema change and at regular intervals using SQLite's backup API or your host's consistent database backup facility. Keep backups private and test restoring one into a separate database. Configure error monitoring and review failed requests.

## Remaining pilot work

The pilot still needs a confirmed route, willing participants, phone/driver verification, account recovery, abuse controls and a support process for missed pickups or damaged goods. Loading, unloading and payment are arranged directly. Sender confirmation records delivery without independently verifying the recipient.

Deployment settings follow the [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/).
