import json
from html import escape as html_escape

from flask import request


class Utils:

    @staticmethod
    def get_response(response, debug_level=None):
        return {
            "success": response.success,
            "statusCode": response.status_code,
            "statusText": response.status_text,
            "errorCode": response.error_code,
            "errorMessage": response.error_message,
            "data": response.response_body,
            "debugTrace": {
                'request': response.debug_request_trace,
                'response': response.debug_response_trace
            } if debug_level is not None and debug_level == 1 else None
        }

    @staticmethod
    def get_callback():
        response = {
            "success": False,
            "statusCode": "",
            "statusText": "",
            "errorCode": "",
            "errorMessage": "",
            "data": None,
            "debugTrace": None
        }

        body_string = request.data.decode('utf-8')  # Equivalent to file_get_contents("php://input")

        if body_string:
            body = json.loads(body_string)  # Decode JSON input

            if 'error' in body and body['error'] and body['error'] != 0:
                response['statusCode'] = body.get('status', "")
                response['statusText'] = body['error']
                response['errorMessage'] = body.get('message', "")
                response['errorCode'] = response['statusCode']
            else:
                response['success'] = True
                response['statusCode'] = 200
                response['statusText'] = "OK"
                response['errorCode'] = 0
                response['data'] = body

        return response
    
    @staticmethod
    def escape(input_data):
        if isinstance(input_data, dict):
            return {key: html_escape(str(value).strip(), quote=True) for key, value in input_data.items()}
        elif isinstance(input_data, list):
            return [html_escape(str(item).strip(), quote=True) for item in input_data]
        return html_escape(str(input_data).strip(), quote=True)

    @staticmethod
    def search_multi_array_by_key_return_keys(array_data, search_key, search_value):
        for item in array_data:
            if item.get(search_key, "").lower() == search_value.lower():
                return item
        return False

    @staticmethod
    def get_callback_response_data_item_value(response_data, item):
        search = Utils.search_multi_array_by_key_return_keys(response_data, "name", item)
        if search:
            return search.get('value', "")
        return ""
