import asyncio
import os

from flask import Flask, jsonify, request
from loguru import logger

from horde import caption_image, generate_image

app = Flask(__name__)


@app.route("/generate")
def generate():
    kwargs = request.get_json()
    code = 200
    data = asyncio.run(generate_image(apikey=os.environ.get("HORDE_API_KEY"), **kwargs))
    if "err" in data:
        code = 400
        logger.error(data)
    return jsonify(data), code


@app.route("/caption")
def caption():
    kwargs = request.get_json()
    code = 200
    data = asyncio.run(caption_image(apikey=os.environ.get("HORDE_API_KEY"), **kwargs))
    if "err" in data:
        code = 400
        logger.error(data)
    return jsonify(data), code


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8886)
