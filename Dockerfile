FROM python:3.12.2-slim AS builder-image

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt .
RUN pip3 install --no-cache-dir wheel
RUN pip3 install --no-cache-dir -r requirements.txt

#* ----------------------------------------------------------------
FROM python:3.12.2-slim AS runner-image

COPY --from=builder-image /venv /venv
RUN mkdir /code
WORKDIR /code
COPY . .

ENV PYTHONUNBUFFERED=1

ENV VIRTUAL_ENV=/venv
ENV PATH="/venv/bin:$PATH"
CMD ["gunicorn","-b", "0.0.0.0:1140", "-w", "4", "-k", "gevent", "--worker-tmp-dir", "/dev/shm", "main:app"]