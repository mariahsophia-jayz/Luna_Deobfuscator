FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN git clone --depth 1 https://github.com/0x251/Prometheus-Deobfuscator.git tools/prometheus-deobfuscator && \
    pip install --no-cache-dir -r tools/prometheus-deobfuscator/requirements.txt

ENV PROMETHEUS_TOOL_DIR=/app/tools/prometheus-deobfuscator

CMD ["python", "luna_bot.py"]
