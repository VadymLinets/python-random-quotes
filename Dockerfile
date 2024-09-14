FROM python:slim AS builder-image

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.cargo/bin/:$PATH"

ADD pyproject.toml pyproject.toml
ADD .python-version .python-version
ADD uv.lock uv.lock
RUN uv sync --frozen


#* ----------------------------------------------------------------
FROM python:slim AS runner-image

COPY --from=builder-image /.venv /.venv
RUN mkdir /code
WORKDIR /code
COPY . .

ENV PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/venv
ENV PATH="/.venv/bin:$PATH"

RUN chmod +x ./scripts/docker/start-server.sh
ENTRYPOINT ["/bin/bash", "./scripts/docker/start-server.sh"]
