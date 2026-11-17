# Imagen del backend (C-04)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY odontologia ./odontologia
COPY tests ./tests

RUN useradd --create-home app
USER app

EXPOSE 8000
CMD ["uvicorn", "odontologia.api:crear_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
