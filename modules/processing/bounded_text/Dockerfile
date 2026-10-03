FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY worker.py server.py ./
USER 65532:65532
EXPOSE 8080
CMD ["python", "-s", "/app/server.py"]
