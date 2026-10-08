# syntax=docker/dockerfile:1
# WMS.KM.WS.Codes (.NET 6) — сервис кодов/DataMatrix (CodesServerApi)
# Build context = ./WmsCodes (опубликованное приложение)
FROM mcr.microsoft.com/dotnet/aspnet:6.0-bookworm-slim AS runtime

# Нативные зависимости:
#  - libgdiplus      — для System.Drawing (GDI+) на Linux
#  - libfontconfig1 / libfreetype6 — для SkiaSharp/ImageSharp (рендер штрихкодов и шрифтов)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgdiplus \
        libfontconfig1 \
        libfreetype6 \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем опубликованное приложение (build context = ./WmsCodes)
COPY . .

# .NET 6 по умолчанию запрещает System.Drawing на Linux — включаем поддержку
RUN sed -i 's/"configProperties": {/"configProperties": {\n      "System.Drawing.EnableUnixSupport": true,/' \
        WMS.KM.WS.Codes.runtimeconfig.json

ENV ASPNETCORE_URLS=http://+:8020

EXPOSE 8020

ENTRYPOINT ["dotnet", "WMS.KM.WS.Codes.dll"]