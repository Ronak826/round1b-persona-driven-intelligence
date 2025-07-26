FROM python:3.10-slim

# ---------- System dependencies ----------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# ---------- Python dependencies ----------
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# ---------- Application setup ----------
WORKDIR /app

# Copy project files into the container
COPY src/ src/
COPY input.json .
COPY run.sh .
COPY approach_explanation.md .
COPY output/ output/

# Make sure the run script is executable
RUN chmod +x run.sh

# ---------- Default command ----------
ENTRYPOINT ["bash", "run.sh"]
