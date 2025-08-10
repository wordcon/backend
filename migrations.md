запустить бд:
docker compose up -d db

сгенерировать миграцию:
docker compose run --rm app litestar database make-migrations -m "your message"

применить миграцию:
docker compose run --rm app litestar database upgrade

ревизия:
docker compose run --rm app litestar database show-current-revision

откатить на 1 шаг:
docker compose run --rm app litestar database downgrade -1
