# Dockerfile to run aws cdk commands
# References
# - AWS CLI https://levelup.gitconnected.com/how-to-create-a-simple-docker-image-with-aws-cli-and-serverless-installed-d1cc2901946

FROM --platform=linux/amd64 alpine:3.16.2

# Install packages
RUN apk update && apk add --update --no-cache \
    git \
    bash \
    curl \
    openssh \
    python3 \
    py3-pip \
    py-cryptography \
    wget \
    curl \
    nodejs \
    npm
RUN apk --no-cache add --virtual builds-deps build-base python3
# Update NPM
RUN npm config set unsafe-perm true
RUN npm update -g
# Install AWSCLI
RUN pip install --upgrade pip && \
    pip install --upgrade awscli
# Install cdk
RUN npm install -g aws-cdk@2.54.0
RUN cdk --version

WORKDIR /app

# Minimum Python App necessary to run pip install
COPY pyproject.toml setup.cfg setup.py README.md ./
RUN mkdir -p /app/src && touch /app/src/__init__.py
RUN pip install -e .[all]

COPY ./ ./
