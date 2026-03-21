# sima-dance-web
Сайт для бронирования мест на концерт

## Production

Сгенерировать production env:

```bash
./scripts/generate_prod_env.sh \
  --email admin@example.com \
  --web-host sima.example.com \
  --api-host api.sima.example.com
```

Скрипт создаст `.env.production` с безопасными случайными значениями для паролей и `DJANGO_SECRET_KEY`.

Запустить деплой:

```bash
./scripts/deploy.sh
```

По умолчанию деплой использует `.env.production`. При необходимости можно передать другой файл:

```bash
./scripts/deploy.sh --env-file /path/to/.env.production
```

После первого деплоя при необходимости создайте администратора:

```bash
DJANGO_SUPERUSER_USERNAME=admin \
DJANGO_SUPERUSER_EMAIL=admin@example.com \
DJANGO_SUPERUSER_PASSWORD='strong-password' \
./scripts/create_superuser.sh
```
