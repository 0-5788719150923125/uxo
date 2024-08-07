ARG SOURCE_IMAGE
FROM $SOURCE_IMAGE

ENV DEBIAN_FRONTEND="noninteractive"
ENV PYTHONPYCACHEPREFIX='/tmp/__pycache__'

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY src/ /src
COPY requirements.txt /src

WORKDIR /src

RUN pip install -r requirements.txt

ENV LOGURU_LEVEL="INFO"

CMD ["python", "app.py"]