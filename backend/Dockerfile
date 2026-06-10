FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

ARG REQUIREMENTS=requirements-cloud.txt
COPY requirements.txt requirements-cloud.txt ./
RUN pip install --no-cache-dir -r ${REQUIREMENTS}

COPY app ./app

CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
