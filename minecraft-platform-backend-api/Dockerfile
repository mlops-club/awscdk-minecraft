FROM python:3.9 AS install
LABEL api_stage=1

COPY . .
RUN touch /usr/bin/config.txt
RUN mkdir logs
RUN pip install . >> logs/pip_install.log 2>&1
# Copy the Python environment we created using our SSH keys

FROM install
LABEL api_stage=2

# Expose our access port
EXPOSE 8000
ARG AWS_PROFILE='mlops-club'
RUN chmod +x /src/minecraft_paas_api/main.py
CMD python /src/minecraft_paas_api/main.py logs/api.log 2>&1
