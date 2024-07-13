FROM python:slim AS builder-image

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir -r requirements.txt

#* ----------------------------------------------------------------
FROM python:slim AS runner-image

COPY --from=builder-image /venv /venv
RUN mkdir /code
WORKDIR /code
COPY . .

ENV PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:$PATH"

RUN chmod +x ./scripts/docker/start-server.sh
ENTRYPOINT ["/bin/bash", "./scripts/docker/start-server.sh"]
