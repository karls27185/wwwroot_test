FROM python:3.12-alpine
WORKDIR /app
COPY app.py .
ENV PORT=8015
ENV SERVICE_NAME=mock
EXPOSE 8015
ENTRYPOINT ["python", "app.py"]