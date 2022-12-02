FROM python:3.10-slim-buster

# CDK and dependencies
WORKDIR /app
RUN apt-get update && apt-get install nodejs
RUN npm install -g aws-cdk

# Application dependencies
# This supports your company's private github repos
# GITHUB_ACCESS_TOKEN should have read-only access to the code.
WORKDIR /app

# Minimum Python App necessary to run pip install
COPY pyproject.toml setup.cfg setup.py ./
RUN mkdir -p /app/src && touch /app/src/__init__.py
RUN pip install -e .[all]

COPY ./ ./

# Run the CDK
RUN cdk deploy
