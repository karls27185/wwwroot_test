-- Создание тестовых БД для WmsAdmin (MSSQL).
-- Схему wmsapi восстанавливают из дампа; схему wmsapi_jobs Hangfire создаёт сам.
IF DB_ID('wmsapi') IS NULL
    CREATE DATABASE wmsapi;
GO
IF DB_ID('wmsapi_jobs') IS NULL
    CREATE DATABASE wmsapi_jobs;
GO