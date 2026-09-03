FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unzip ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deno.land/install.sh | sh

ENV DENO_INSTALL=/root/.deno
ENV PATH=/root/.deno/bin:$PATH

RUN ln -s /root/.deno/bin/deno /usr/local/bin/deno

RUN pip install --no-cache-dir Flask gunicorn requests yt-dlp

WORKDIR /app
COPY . .

CMD ["sh", "-c", "deno --version && yt-dlp --version && gunicorn --bind 0.0.0.0:${PORT:-10000} app:app"]
