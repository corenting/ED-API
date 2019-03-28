from flask import jsonify


def get_response(res_data):
    response = jsonify(res_data)
    if res_data is not None and 'error' in res_data:
        response.status_code = 402
    return response


def error_response(msg):
    return {
        'error': msg
}