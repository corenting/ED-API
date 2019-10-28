from flask import jsonify


def error_response(msg, status_code=400):
    return jsonify({"error": msg}), status_code
