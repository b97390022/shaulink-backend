FROM python:3.11.3-slim-bullseye

WORKDIR /shaulink-backend

RUN echo "[Install basics...]"   && \
    apt-get update && apt-get install -y curl && \
    echo "[Clean up...]" && \
    rm -rf /var/lib/apt/lists/*
    
COPY requirements.txt /shaulink-backend/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY src /shaulink-backend/src

EXPOSE 8000

CMD [ "python", "-m", "src.main" ]