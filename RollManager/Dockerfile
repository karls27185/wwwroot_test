# syntax=docker/dockerfile:1
# WMS.KM.WS.RollManager (.NET 7) — веб-UI учёта рулонов
# Build context = ./RollManager (опубликованное приложение)
FROM mcr.microsoft.com/dotnet/aspnet:7.0-bookworm-slim AS runtime

# Нативные зависимости:
#  - libfontconfig1 / libfreetype6 — для ImageSharp (рендер шрифтов)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libfontconfig1 \
        libfreetype6 \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копируем опубликованное приложение (build context = ./RollManager)
COPY . .

# ВНИМАНИЕ: начиная с .NET 7 System.Drawing.Common не поддерживается на Linux
# (переключатель System.Drawing.EnableUnixSupport удалён), поэтому он здесь не включается.

ENV ASPNETCORE_URLS=http://+:8036

EXPOSE 8036

ENTRYPOINT ["dotnet", "WMS.KM.WS.RollManager.dll"]