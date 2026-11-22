FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd --create-home app && mkdir /data && chown app:app /data /app
COPY --chown=app:app . .
USER app
RUN python manage.py collectstatic --noinput
ENV FASAL_DEBUG=0 FASAL_DATABASE_PATH=/data/db.sqlite3
VOLUME ["/data"]
EXPOSE 8000
CMD ["sh", "deploy/start.sh"]
