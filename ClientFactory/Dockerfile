# syntax=docker/dockerfile:1
# ClientFactoryWMS (.NET 7) — веб-UI рабочего места (камера/маркировка)
# Build context = ./ClientFactory (опубликованное приложение)
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

# Копируем опубликованное приложение (build context = ./ClientFactory)
COPY . .

# ВНИМАНИЕ: начиная с .NET 7 System.Drawing.Common не поддерживается на Linux
# (переключатель System.Drawing.EnableUnixSupport удалён), поэтому он здесь не включается.

ENV ASPNETCORE_URLS=http://+:8060

EXPOSE 8060

ENTRYPOINT ["dotnet", "ClientFactoryWMS.dll"]