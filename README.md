# WMS.KM.WS

Комплекс приложений для складского учёта, маркировки и прослеживаемости продукции
(работа с кодами DataMatrix, агрегация в упаковки, учёт рулонов, работа с камерами
технического зрения и интеграция с внешними сервисами: центральный сервер (ERP),
сервис печати этикеток и CRPT-прокси).

Все сервисы поставляются как опубликованные .NET-приложения и запускаются в Docker.

---

## Состав проекта

| Каталог | Приложение | DLL | .NET | Порт | Назначение |
|---|---|---|---|---|---|
| `WmsAdmin/` | WMS.KM.WS.Admin | `WMS.KM.WS.Admin.dll` | 6.0 | 8080 | Админка/API, агрегация, SignalR-хабы, Hangfire-задачи |
| `WmsCodes/` | WMS.KM.WS.Codes | `WMS.KM.WS.Codes.dll` | 6.0 | 8020 | Сервис кодов/DataMatrix (CodesServerApi) |
| `RollManager/` | WMS.KM.WS.RollManager | `WMS.KM.WS.RollManager.dll` | 7.0 | 8036 | Веб-UI учёта рулонов |
| `ClientFactory/` | ClientFactoryWMS | `ClientFactoryWMS.dll` | 7.0 | 8060 | Веб-UI рабочего места (камера/маркировка) |
| `CameraService/` | CognexWorkerService.Blazor | `WMS.KM.WS.CognexWorkerService.Blazor.dll` | 9.0 | 8070 | Сервис камер (Cognex/Hikrobot), SignalR CameraHub |

> Каталоги содержат **опубликованные** приложения (есть `*.deps.json`/`*.runtimeconfig.json`,
> но нет `*.csproj`). Dockerfile копирует содержимое каталога целиком.

### Архитектура взаимодействия

```
                        ┌────────────────────┐
                        │   Central (ERP)    │  :8015  (внешний)
                        └─────────▲──────────┘
                                  │ getassemblies / confirmassembly / completeassembly
                                  │ getdatamatrix / GetCameraSessions / AddProducts
        ┌─────────────────────────┼───────────────────────────┐
        │                         │                           │
┌───────┴────────┐      ┌─────────┴────────┐         ┌────────┴─────────┐
│   WmsAdmin     │─────▶│    WmsCodes      │         │  CameraService   │
│ :8080 (MSSQL)  │ :8020│ :8020 (Postgres) │         │ :8070            │
└───▲────────▲───┘      └─────────▲────────┘         └────────▲─────────┘
    │        │                    │                           │
    │        │      ┌─────────────┴───────────┐               │
    │        └──────│      RollManager        │               │
    │   (API)       │      :8036              │               │
    └───────────────│  ClientFactory :8060    ┼───────────────┘
                    └─────────────────────────┘
```

Внешние интеграции:

| Настройка | Назначение | Прод (пример) |
|---|---|---|
| `CENTRAL_HOST` | Центральный сервер (ERP) | `192.168.10.56:8015` |
| `PRINTPACK_HOST` | Сервис печати упаковки | `192.168.41.1:8040` |
| `CRPT_PROXY_URL` | CRPT-прокси / ЧЗ True API | `http://192.168.10.226:5050/` |

Базы данных:

| Модуль | СУБД | База(ы) |
|---|---|---|
| WmsAdmin | SQL Server | `wmsapi` (данные), `wmsapi_jobs` (Hangfire) |
| WmsCodes | PostgreSQL | `wmsCodes` |
| Остальные | — | обращаются к API WmsAdmin/WmsCodes |

---

## Структура репозитория

```
.
├── docker-compose.yml          # сервисы приложений + тестовые эмуляторы
├── .env                        # переменные окружения (порты, строки подключения)
├── docker/
│   ├── mock-api/               # универсальный мок (central / printpack / crpt)
│   │   ├── app.py
│   │   └── Dockerfile
│   └── mssql/
│       └── init.sql            # создание БД wmsapi / wmsapi_jobs
├── WmsAdmin/{Dockerfile, appsettings.json, ...}
├── WmsCodes/{Dockerfile, appsettings.json, ...}
├── RollManager/{Dockerfile, appsettings.json, ...}
├── ClientFactory/{Dockerfile, appsettings.json, ...}
└── CameraService/{Dockerfile, appsettings.json, ...}
```

---

## Требования

- Docker Engine 24+ и Docker Compose v2 (`docker compose ...`).
- Свободные порты: `8080`, `8020`, `8036`, `8060`, `8070`, `1433`, `5432`, `8015`, `8040`, `5050`.
- Для продакшена — доступ к внешним сервисам (ERP/печать/CRPT) и к серверам БД.

---

## Быстрый старт (тестовое окружение)

Тестовое окружение поднимает **эмуляторы** внешних зависимостей, чтобы приложения
запускались автономно, без реального ERP, сервера печати, CRPT и внешних БД.

### 1. Подготовка `.env`

Файл `.env` уже настроен на тестовый режим (БД и внешние сервисы указывают на контейнеры):

```dotenv
DB_DEFAULT_CONNECTION=Server=mssql,1433;Database=wmsapi;...
DB_HANGFIRE_CONNECTION=Server=mssql,1433;Database=wmsapi_jobs;...
DB_CODES_CONNECTION=Host=postgres;Port=5432;Database=wmsCodes;...
CENTRAL_HOST=central-mock
PRINTPACK_HOST=printpack-mock
CRPT_PROXY_URL=http://crpt-mock:5050/
```

### 2. Запуск

```bash
docker compose up -d --build
```

Будут подняты:

| Контейнер | Роль | Порт (host) |
|---|---|---|
| `wmsadmin` | WmsAdmin | 8080 |
| `wmscodes` | WmsCodes | 8020 |
| `rollmanager` | RollManager | 8036 |
| `clientfactory` | ClientFactory | 8060 |
| `cameraservice` | CameraService | 8070 |
| `wms-mssql` | SQL Server (эмулятор) | 1433 |
| `wms-mssql-init` | one-shot: создаёт `wmsapi`, `wmsapi_jobs` | — |
| `wms-postgres` | PostgreSQL (эмулятор) | 5432 |
| `wms-central-mock` | Мок ERP | 8015 |
| `wms-printpack-mock` | Мок печати | 8040 |
| `wms-crpt-mock` | Мок CRPT-прокси | 5050 |

### 3. Проверка

```bash
docker compose ps
docker compose logs mssql-init        # ожидаемо: "mssql-init: databases are ready"

curl http://localhost:8015/health     # {"status":"ok","service":"central-mock"}
curl http://localhost:8015/api/ws/getdatamatrix   # []
curl http://localhost:5050/api/v3/true-api/auth/token   # {"token":"mock-token",...}
```

Интерфейсы приложений:

- WmsAdmin: http://localhost:8080
- WmsCodes (Swagger): http://localhost:8020/swagger
- RollManager: http://localhost:8036
- ClientFactory: http://localhost:8060
- CameraService: http://localhost:8070

### 4. Работа с базами

```bash
# SQL Server
docker exec -it wms-mssql /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P P@ssw0rd -C \
  -Q "SELECT name FROM sys.databases"

# PostgreSQL
docker exec -it wms-postgres psql -U postgres -l
```

> **Важно:** приложения не создают схему БД (`UseAutoMigration=false`).
> `wmsapi_jobs` (Hangfire) и `wmsCodes` создаются/мигрируются самими сервисами,
> а схему `wmsapi` нужно **восстановить из дампа**:

```bash
docker cp dump_wmsapi.bak wms-mssql:/tmp/dump_wmsapi.bak
docker exec -it wms-mssql /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P P@ssw0rd -C \
  -Q "RESTORE DATABASE wmsapi FROM DISK='/tmp/dump_wmsapi.bak' WITH REPLACE, MOVE 'wmsapi' TO '/var/opt/mssql/data/wmsapi.mdf', MOVE 'wmsapi_log' TO '/var/opt/mssql/data/wmsapi_log.ldf'"
```

### 5. Остановка

```bash
docker compose down            # остановить
docker compose down -v         # остановить и удалить данные БД (тома)
```

---

## Запуск в продакшене

В продакшене приложения подключаются к **реальным** БД и внешним сервисам,
а эмуляторы не используются.

### 1. `.env` для продакшена

Раскомментируйте прод-значения (примеры уже есть в `.env`):

```dotenv
# Внешние сервисы
CENTRAL_HOST=192.168.10.56
PRINTPACK_HOST=192.168.41.1
CRPT_PROXY_URL=http://192.168.10.226:5050/

# Базы данных
DB_DEFAULT_CONNECTION=Server=192.168.41.1,1415;Database=wmsapi;User Id=sa;Password=<ПАРОЛЬ>;TrustServerCertificate=True;Encrypt=False;
DB_HANGFIRE_CONNECTION=Server=192.168.41.1,1415;Database=wmsapi_jobs;User Id=sa;Password=<ПАРОЛЬ>;TrustServerCertificate=True;Encrypt=False;
DB_CODES_CONNECTION=Host=192.168.41.1;Port=5432;Database=wmsCodes;Username=postgres;Password=<ПАРОЛЬ>
```

> В продакшене смените пароли по умолчанию и не храните `.env` в системе контроля версий.

### 2. Запуск только приложений (без эмуляторов)

Поднимайте только нужные сервисы, исключив моки:

```bash
docker compose up -d --build \
  wmsadmin wmscodes rollmanager clientfactory cameraservice
```

Эмуляторы (`mssql`, `mssql-init`, `postgres`, `central-mock`, `printpack-mock`, `crpt-mock`)
при этом не запускаются; зависимости `depends_on` для них не мешают, т.к. эти сервисы
не запрашиваются явно.

Если требуется полностью убрать моки из проекта — удалите соответствующие сервисы
из `docker-compose.yml` и каталог `docker/mock-api`.

### 3. Проверка после запуска

```bash
docker compose ps
docker compose logs -f wmsadmin
curl -I http://localhost:8080
```

### 4. Обновление версий

Версии приложений заданы в `image:` в `docker-compose.yml`:

```
wmsadmin:2.6.30.129
wmscodes:1.6.11.5
rollmanager:1.7.6.9
clientfactory:2.7.30.33
cameraservice:2.9.6.5
```

При выпуске новой версии:
1. обновите опубликованные файлы в соответствующем каталоге;
2. при необходимости измените тег `image:`;
3. пересоберите: `docker compose build <service> && docker compose up -d <service>`.

---

## Конфигурация

### Приоритет настроек

Значения в `appsettings.json` переопределяются переменными окружения контейнера
(двойное подчёркивание = вложенность), затем — переменными из `.env`:

```
appsettings.json  <  environment: в docker-compose  <  .env (подстановка ${VAR})
```

Пример: `ConnectionStrings__DefaultConnection` переопределяет
`ConnectionStrings:DefaultConnection` из `appsettings.json`.

### Ключевые переменные (`.env`)

| Переменная | Назначение | Тест | Прод |
|---|---|---|---|
| `WMSADMIN_HTTP_PORT` | Порт WmsAdmin | 8080 | 8080 |
| `WMSCODES_HTTP_PORT` | Порт WmsCodes | 8020 | 8020 |
| `ROLLMANAGER_HTTP_PORT` | Порт RollManager | 8036 | 8036 |
| `CLIENTFACTORY_HTTP_PORT` | Порт ClientFactory | 8060 | 8060 |
| `CAMERASERVICE_HTTP_PORT` | Порт CameraService | 8070 | 8070 |
| `DB_DEFAULT_CONNECTION` | БД данных WmsAdmin (MSSQL) | `mssql,1433` | внешний сервер |
| `DB_HANGFIRE_CONNECTION` | БД Hangfire (MSSQL) | `mssql,1433` | внешний сервер |
| `DB_CODES_CONNECTION` | БД WmsCodes (PostgreSQL) | `postgres:5432` | внешний сервер |
| `CENTRAL_HOST` | Центральный сервер | `central-mock` | `192.168.10.56` |
| `PRINTPACK_HOST` | Сервис печати | `printpack-mock` | `192.168.41.1` |
| `CRPT_PROXY_URL` | CRPT-прокси | `http://crpt-mock:5050/` | `http://192.168.10.226:5050/` |

---

## Тестовые эмуляторы

Все моки реализованы одним образом `wms-mock-api` (`docker/mock-api`) и различаются
только `SERVICE_NAME`/`PORT`. Мок отвечает `200` + валидным JSON на любой путь:

- `GET` со словами `list/sessions/assemblies/products/datamatrix/get` → `[]`
- пути со `token/auth/login` → объект с `token`
- `/health`, `/ping`, `/` → `{"status":"ok","service":"<имя>"}`
- остальное → `{}`

Точные контракты внешних сервисов в моках не воспроизведены — при необходимости
структуру ответа можно задать в `docker/mock-api/app.py` (`_payload`).

---

## Устранение неполадок

| Проблема | Решение |
|---|---|
| `failed to resolve reference "mcr.microsoft.com/mssql-tools18:latest"` | Уберите отдельный образ `mssql-tools18`; `mssql-init` должен использовать `mcr.microsoft.com/mssql/server:2022-latest` (sqlcmd лежит в `/opt/mssql-tools18/bin/`). |
| `mssql-init` падает | Проверьте `docker compose logs mssql`, дождитесь healthy; проверьте пароль `MSSQL_SA_PASSWORD`. |
| Приложение не видит БД | Внутри сети используются имена контейнеров (`mssql`, `postgres`), а не `localhost`. Для внешних хостов добавьте `host.docker.internal`/IP. |
| Порт занят | Измените соответствующий `*_HTTP_PORT` в `.env`. |
| WmsCodes не стартует | Проверьте доступность PostgreSQL и корректность `DB_CODES_CONNECTION`. |
| Печать/SkiaSharp не работает на Linux | Для WmsAdmin нужен нативный `libSkiaSharp.so` (`SkiaSharp.NativeAssets.Linux` в проекте при публикации). |

---

## Замечания по платформам

- **WmsAdmin, WmsCodes (.NET 6):** включена поддержка `System.Drawing` на Linux
  (`System.Drawing.EnableUnixSupport`), установлен `libgdiplus`.
- **RollManager, ClientFactory (.NET 7):** `System.Drawing.Common` на Linux с .NET 7+
  не поддерживается — в Dockerfile соответствующий переключатель не включается.
- **CameraService (.NET 9):** SDK Cognex DataMan ориентирован преимущественно на Windows.
  Linux-образ рассчитан на работу с камерами по TCP/IP (`HikrobotSettings:TcpSendPort`).
  Для нативного доступа к камерам Cognex требуются Windows-контейнеры.