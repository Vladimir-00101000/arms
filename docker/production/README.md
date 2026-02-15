Создайте .env файл из .env.example (менять ничего не нужно)

--------------------------------------------------------------------------------------------------

Запуск контейнеров:
docker compose up
или
docker compose up -d (запускаются в фоновом режиме)

Проверить:
docker ps

```bash
dev git:(kiselev-dev) ✗ docker ps
CONTAINER ID   IMAGE                                      COMMAND                  CREATED          STATUS          PORTS                                         NAMES
744c7a692235   nginx:alpine                               "/docker-entrypoint.…"   34 minutes ago   Up 34 minutes   0.0.0.0:80->80/tcp, [::]:80->80/tcp           app-nginx
a5638324be7f   quay.io/oauth2-proxy/oauth2-proxy:latest   "/bin/oauth2-proxy"      34 minutes ago   Up 34 minutes   0.0.0.0:4180->4180/tcp, [::]:4180->4180/tcp   app-oauth2
5c947e58862d   postgres:15-alpine                         "docker-entrypoint.s…"   34 minutes ago   Up 34 minutes   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp   app-postgresql
7da5bace5db3   production-app-api                         "uvicorn src.main:ap…"   34 minutes ago   Up 34 minutes   0.0.0.0:8000->8000/tcp, [::]:8000->8000/tcp   app-api
```

Удалить контейнеры вместе с томами:
docker compose down -v

Создавать таблицы через alembic:

docker compose exec app-api bash
alembic revision --autogenerate -m "Initial tables"
alembic upgrade head

--------------------------------------------------------------------------------------------------
