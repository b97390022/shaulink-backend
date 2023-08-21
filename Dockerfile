FROM python:3.11.3-slim-bullseye as base

RUN echo "[Install basics...]"   && \
    apt-get update && apt-get install -y curl gcc && \
    echo "[Clean up...]" && \
    rm -rf /var/lib/apt/lists/*

ENV BASE_DIR=/shaulink-backend
WORKDIR ${BASE_DIR}

FROM base AS test

COPY poetry.lock ${BASE_DIR}/poetry.lock
COPY pyproject.toml ${BASE_DIR}/pyproject.toml
RUN pip install poetry && poetry export --without-hashes --format=requirements.txt > ${BASE_DIR}/requirements.txt


FROM base AS build
COPY --from=test ${BASE_DIR}/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY src ${BASE_DIR}/src
COPY temp ${BASE_DIR}/temp

EXPOSE 8000

CMD [ "python", "-m", "src.main" ]