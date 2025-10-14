FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# deps del sistema (psycopg2, build)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# requirements primero para cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiar proyecto
COPY . .

# crear usuario no root
RUN useradd -ms /bin/bash django && chown -R django:django /app
USER django

# collectstatic en build (puede hacerse también en entrypoint)
RUN python manage.py collectstatic --noinput || true

# gunicorn a 0.0.0.0:8000
EXPOSE 8000
CMD ["gunicorn", "diplomaturas.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
