### Dev
```bash
cp .env.docker.example .env
```

```bash
docker compose up --build
```

- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health/
- Prometheus metrics: http://localhost:8000/metrics

Остановить:
```bash
docker compose down
```

Полностью очистить (с томами):
```bash
docker compose down -v
```

### Prod
```bash
cp .env.docker.example .env
```
```bash
docker compose -f docker-compose.yml up -d --build
```

Остановить:
```bash
docker compose -f docker-compose.yml down
```

### Infra (только база данных)
```bash
docker compose -f deploy/docker-compose.infra.yml up -d
```

Остановить инфраструктуру:
```bash
docker compose -f deploy/docker-compose.infra.yml down
```

## Наблюдаемость

Запуск dev + наблюдаемость:
```bash
docker compose \
  -f docker-compose.yml \
  -f docker-compose.override.yml \
  -f deploy/docker-compose.observability.yml \
  up --build
```

- Jaeger UI: http://localhost:16686
- Pyroscope UI: http://localhost:4040