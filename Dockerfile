FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt /tmp/backend.txt
COPY frontend/requirements.txt /tmp/frontend.txt
RUN pip install --no-cache-dir -r /tmp/backend.txt -r /tmp/frontend.txt
COPY . /app
ENV PYTHONPATH=/app/backend
CMD ["uvicorn","app.main:app","--app-dir","backend","--host","0.0.0.0","--port","8000"]
