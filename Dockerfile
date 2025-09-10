FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /app

# Dependencias
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Código
COPY . /app
ENV PYTHONPATH=/app

# Sanidad opcional
RUN python -c "import sys, dagster; print('Python:', sys.version); print('Dagster:', dagster.__version__)"