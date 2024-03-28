from uvicorn.workers import UvicornWorker


class CustomUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "host": "0.0.0.0",
        "port": 443,
        "ssl_keyfile": "/etc/letsencrypt/live/media.sheppsu.me/privkey.pem",
        "ssl_certfile": "/etc/letsencrypt/live/media.sheppsu.me/fullchain.pem"
    }
