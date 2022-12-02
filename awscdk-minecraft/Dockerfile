FROM python:3.10-buster

# CDK and dependencies
WORKDIR /app

RUN apt-get update && \
 apt-get install -y \
    nodejs npm

RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
 apt-get install -y nodejs
RUN npm install -g aws-cdk@2.45.x

# Minimum Python App necessary to run pip install
COPY pyproject.toml setup.cfg setup.py ./
RUN mkdir -p /app/src && touch /app/src/__init__.py
RUN pip install -e .[all]

COPY ./ ./

# Run the CDK
RUN cdk deploy
