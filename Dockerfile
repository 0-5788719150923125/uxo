FROM python:3.12-slim

ENV DEBIAN_FRONTEND="noninteractive"
ENV PYTHONPYCACHEPREFIX='/tmp/__pycache__'

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src

COPY src/ /src
COPY requirements.txt /src

RUN pip install -r requirements.txt

CMD ["python", "main.py"]