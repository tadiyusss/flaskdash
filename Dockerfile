FROM node:24-slim AS assets
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=assets /app/core/static /app/core/static
COPY --from=assets /usr/local/bin/node /usr/local/bin/node
COPY --from=assets /app/node_modules /app/node_modules
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "-k", "geventwebsocket.gunicorn.workers.GeventWebSocketWorker", "-w", "1", "run:app"]
