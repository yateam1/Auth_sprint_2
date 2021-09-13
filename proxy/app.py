from flask import Flask, jsonify, abort, request, Response
import pybreaker
import json
import requests
from requests import get
import os

SITE_NAME = f"http://{os.environ['FLASK_API']}:5000/"

app = Flask(__name__)
app.config['SECRET_KEY'] = "Secret!"

FAILURES=3
TIMEOUT=6

circuit = pybreaker.CircuitBreaker(fail_max=FAILURES, reset_timeout=TIMEOUT, name="proxy")

@circuit
@app.route('/', defaults={'path': ''}, methods=["GET", "POST"])
@app.route('/<path:path>', methods=["GET", "POST"])
def proxy(*args, **kwargs):

    if request.method=='POST':
        url = request.url.replace(request.host_url, SITE_NAME)
        resp = requests.post(url, json=request.get_json(), headers=dict(request.headers))
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response
    elif request.method=='DELETE':
        url = request.url.replace(request.host_url, SITE_NAME)
        resp = requests.delete(url, headers=dict(request.headers)).content
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        response = Response(resp.content, resp.status_code, headers)
        return response

    resp = requests.request(
        method=request.method,
        url=request.url.replace(request.host_url, SITE_NAME),
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5023, debug=True)