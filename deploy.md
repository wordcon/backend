dev:
cp .env.docker.example .env
docker compose up --build

prod:
cp .env.docker.example .env
docker compose -f docker-compose.yml up --build

infra:
docker compose -f deploy/docker-compose.infra.yml up -d