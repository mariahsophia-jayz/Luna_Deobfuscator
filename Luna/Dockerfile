FROM python:3.11-slim

# Java is needed to run the underlying deobfuscator jars
RUN apt-get update && \
    apt-get install -y --no-install-recommends default-jre-headless && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# jars/LuraphDeobfuscator.jar and jars/unluac.jar must already exist in the
# repo — download them yourself and commit them.
COPY . .

ENV LURAPH_JAR_PATH=/app/jars/LuraphDeobfuscator.jar
ENV UNLUAC_JAR_PATH=/app/jars/unluac.jar

CMD ["python", "luna_bot.py"]
