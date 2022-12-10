from mangum import Mangum
from minecraft_paas_api.app import app

handler = Mangum(app)
