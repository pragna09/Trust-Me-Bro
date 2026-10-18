FROM python:3.11-slim
WORKDIR /app
# Build tools only needed if a wheel is missing for s390x and pip must compile from source
RUN apt-get update && apt-get install -y --no-install-recommends build-essential gfortran libopenblas-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY core.py app.py model.joblib metrics.json ./
COPY static ./static
COPY data/replay.csv ./data/replay.csv
RUN useradd -m -u 1000 app && chown -R app /app
USER app
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
