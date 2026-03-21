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

Первый деплой с созданием события и установкой цен:

```bash
./scripts/init_deploy.sh
```

При необходимости можно передать параметры создания события в `set_prices.py`:

```bash
./scripts/init_deploy.sh \
  --event-title "Концерт 2026" \
  --event-date 2026-04-01 \
  --event-image-url https://example.com/poster.jpg
```

Обычный деплой/редеплой без создания нового события:

```bash
./scripts/deploy.sh
```

По умолчанию `deploy.sh` использует `.env.production` и после запуска контейнеров автоматически выполняет `set_prices` в режиме обновления цен без создания нового события.

При необходимости можно передать другой env-файл:

```bash
./scripts/deploy.sh --env-file /path/to/.env.production
```

Если нужно пропустить автоматическое обновление цен:

```bash
./scripts/deploy.sh --skip-set-prices
```

Обновить код из `origin/main` и сразу выполнить редеплой:

```bash
./scripts/update_redeploy.sh
```

Скрипт делает `git fetch`, `git checkout main`, `git pull --ff-only` и затем запускает `deploy.sh`. Если рабочее дерево грязное, он остановится, чтобы не затереть локальные изменения.

После первого деплоя при необходимости создайте администратора:

```bash
DJANGO_SUPERUSER_USERNAME=admin \
DJANGO_SUPERUSER_EMAIL=admin@example.com \
DJANGO_SUPERUSER_PASSWORD='strong-password' \
./scripts/create_superuser.sh
```
