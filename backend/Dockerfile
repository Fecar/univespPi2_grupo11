FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

# NOTE: REMOVER O '--reload' DO CMD ABAIXO:
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--reload", "app:app"]
