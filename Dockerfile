FROM node:24-alpine AS assets
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AUTO_INSTALL_EXTENSION_DEPS=false
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN for f in extensions/*/requirements.txt; do [ -f "$f" ] && pip install --no-cache-dir -r "$f"; done || true
COPY --from=assets /app/core/static /app/core/static
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "1", "run:app"]
