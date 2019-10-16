from flask import request


def get_requests_headers():
    return {"User-Agent": "ED-API"}


def request_param(name, default_value=0):
    value = request.args.get(name, default_value)
    if isinstance(default_value, int):
        if isinstance(value, str):
            if value.isdigit():
                value = int(value)
    return value
