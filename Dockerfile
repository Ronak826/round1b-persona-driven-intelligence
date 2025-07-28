FROM python:3.10-slim


RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY src/ ./src/
COPY input/ ./input/
COPY output/ ./output/
COPY approach_explanation.md .


ENTRYPOINT ["python", "-u", "src/main_all.py"]
