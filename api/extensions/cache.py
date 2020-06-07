from flask_caching import Cache

cache = Cache(config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "/tmp/ed-api/"})


def init_cache(app):
    cache.init_app(app)
