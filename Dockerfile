FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN touch users.sqlite3 && chmod 666 users.sqlite3

ENV PORT 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
