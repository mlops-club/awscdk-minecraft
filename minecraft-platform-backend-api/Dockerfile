FROM python:3.9 AS install
LABEL api_stage=1

WORKDIR /app
COPY setup.cfg setup.py ./
COPY src/minecraft_paas_api/__init__.py ./src/minecraft_paas_api/

RUN touch /usr/bin/config.txt
RUN mkdir /logs
RUN pip install -e . >> /logs/pip_install.log 2>&1
# Copy the Python environment we created using our SSH keys

FROM install
LABEL api_stage=2
COPY . .


# Expose our access port
EXPOSE ${DEV_PORT}
CMD uvicorn "minecraft_paas_api.main:create_default_app" --reload --factory --workers 1 --host 0.0.0.0 --port ${DEV_PORT}
