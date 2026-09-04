FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl unzip ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Deno
RUN curl -fsSL https://deno.land/install.sh | sh

ENV DENO_INSTALL=/root/.deno
ENV PATH=/root/.deno/bin:$PATH

# Make Deno available system-wide
RUN ln -sf /root/.deno/bin/deno /usr/local/bin/deno

# Install Python packages
RUN pip install --no-cache-dir \
    Flask \
    gunicorn \
    requests \
    "yt-dlp[default]"

WORKDIR /app

COPY . .

# Check Deno and yt-dlp before starting
CMD ["sh", "-c", "deno --version && yt-dlp --version && gunicorn --bind 0.0.0.0:${PORT:-10000} app:app"]
