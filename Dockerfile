FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ⚠️ No recomendado hardcodear secretos en la imagen
# ENV APP_PASSWORD="SuperSecret123!"

WORKDIR /app

# requirements ahora está en la raíz del repo
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# el código sigue dentro de app/
COPY app/ ./app/

EXPOSE 5005
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5005"]

