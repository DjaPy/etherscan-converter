import uvicorn

from etherscan_converter.config import config
from etherscan_converter.entrypoints.http_server import app_server

if __name__ == '__main__':
    uvicorn.run(app_server, host=config.host, port=config.port)
