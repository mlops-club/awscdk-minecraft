FROM python:3.10.3-slim-bullseye

# install dumb-init for cleaner signal handling
RUN apt-get update && apt-get install -yqq \
    dumb-init \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir --upgrade pip
RUN pip install boto3 mypy_boto3_s3

ENTRYPOINT ["dumb-init", "--"]