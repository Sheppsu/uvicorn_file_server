from uvicorn.workers import UvicornWorker


class CustomUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {
        "host": "127.0.0.1",
        "port": 8727,
        "ssl_keyfile": "/etc/letsencrypt/live/media.sheppsu.me/privkey.pem",
        "ssl_certfile": "/etc/letsencrypt/live/media.sheppsu.me/fullchain.pem"
    }
