from flask import jsonify
from models.exceptions.api_exception import ApiException


def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def register_error_handler(app):
    app.register_error_handler(ApiException.status_code, handle_invalid_usage)
