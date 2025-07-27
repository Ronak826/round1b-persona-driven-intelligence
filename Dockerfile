FROM python:3.10-slim

# ---------- System dependencies ----------
# Install necessary system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# ---------- Python dependencies ----------
# Copy only the requirements file first to leverage Docker's layer caching.
# This step will only re-run if requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Application setup ----------
# Now, copy the rest of the project files into the container
COPY src/ ./src/
COPY input.json .
COPY run.sh .
COPY approach_explanation.md .
COPY output/ ./output/
COPY input/ ./input/

# Make the run script executable
RUN chmod +x run.sh

# ---------- Default command ----------
# Set the entrypoint to run the script when the container starts
ENTRYPOINT ["python", "-u", "src/main.py", "--config", "input.json", "--output", "output/challenge1b_output.json"]
