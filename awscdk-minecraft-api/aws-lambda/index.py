from mangum import Mangum
from fastapi import FastAPI
from minecraft_paas_api.main import create_default_app


APP: FastAPI = create_default_app()
handler = Mangum(APP)
