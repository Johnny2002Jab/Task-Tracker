# Builder stage: install dependencies into a venv-like prefix
FROM python:3.13-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime stage: slim image, only what's needed to run the app
FROM python:3.13-slim AS runtime

RUN useradd --create-home --shell /usr/sbin/nologin app

WORKDIR /app

COPY --from=builder /install /usr/local
COPY app ./app

RUN chown -R app:app /app

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
