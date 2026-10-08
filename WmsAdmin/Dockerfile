# syntax=docker/dockerfile:1
# WMS.KM.WS.Admin (.NET 6) — админка/API (WMSServerApi, SignalR-хабы)
# Build context = ./WmsAdmin (опубликованное приложение)
FROM mcr.microsoft.com/dotnet/aspnet:6.0-bookworm-slim AS runtime

# Нативные зависимости:
#  - libgdiplus      — для System.Drawing (GDI+) на Linux
#  - libfontconfig1 / libfreetype6 — для SkiaSharp (ZXing.Net.Bindings.SkiaSharp) и шрифтов
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgdiplus \
        libfontconfig1 \
        libfreetype6 \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем опубликованное приложение (build context = ./WmsAdmin)
COPY . .

# .NET 6 по умолчанию запрещает System.Drawing на Linux — включаем поддержку
RUN sed -i 's/"configProperties": {/"configProperties": {\n      "System.Drawing.EnableUnixSupport": true,/' \
        WMS.KM.WS.Admin.runtimeconfig.json

ENV ASPNETCORE_URLS=http://+:8080

EXPOSE 8080

ENTRYPOINT ["dotnet", "WMS.KM.WS.Admin.dll"]