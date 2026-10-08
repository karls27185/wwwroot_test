# syntax=docker/dockerfile:1
# WMS.KM.WS.CognexWorkerService.Blazor (.NET 9) — сервис камер (Cognex/Hikrobot), SignalR CameraHub
# Build context = ./CameraService (опубликованное приложение)
FROM mcr.microsoft.com/dotnet/aspnet:9.0-bookworm-slim AS runtime

# Нативные зависимости:
#  - libfontconfig1 / libfreetype6 — шрифты для Blazor-UI/рендера
#  - ca-certificates              — доверенные сертификаты для интеграций
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libfontconfig1 \
        libfreetype6 \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем опубликованное приложение (build context = ./CameraService)
COPY . .

# ВНИМАНИЕ: SDK Cognex DataMan ориентирован в первую очередь на Windows.
# При работе через TCP/IP (HikrobotSettings:TcpSendPort) образ на Linux подходит.
# Если нужен нативный доступ к камерам через Windows — используйте Windows-контейнеры.

ENV ASPNETCORE_URLS=http://+:8070

EXPOSE 8070

ENTRYPOINT ["dotnet", "WMS.KM.WS.CognexWorkerService.Blazor.dll"]