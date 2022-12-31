FROM python:3.10.3-slim-bullseye

# install dumb-init for cleaner signal handling
# RUN apt-get update && apt-get install -yqq \
#     dumb-init \
#     && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/*
# RUN pip install --no-cache-dir --upgrade pip
# RUN pip install boto3 mypy_boto3_s3

# ENTRYPOINT ["dumb-init", "--"]


# install the aws cli v2
RUN apt-get update && apt-get install -y zip curl

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install

WORKDIR /app
COPY  ./ /app

ENTRYPOINT ["/bin/bash", "backup-or-restore-s3.sh"]
