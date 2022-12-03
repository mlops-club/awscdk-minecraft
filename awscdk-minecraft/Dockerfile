FROM alpine:3.16.2

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
RUN npm install -g aws-cdk
RUN cdk --version
ENTRYPOINT []

WORKDIR /app

# Minimum Python App necessary to run pip install
COPY pyproject.toml setup.cfg setup.py ./
RUN mkdir -p /app/src && touch /app/src/__init__.py
RUN pip install -e .[all]

# symlink python to /usr/bin/python3
RUN ln -sf /usr/bin/python3 /usr/bin/python
CMD cdk deploy --app 'python app.py'
