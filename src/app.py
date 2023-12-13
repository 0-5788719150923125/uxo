import asyncio
import os
import traceback

from flask import Flask, jsonify, request
from loguru import logger

from horde import caption_image, generate_image

app = Flask(__name__)


@app.route("/generate")
def generate():
    kwargs = request.get_json()
    data = asyncio.run(generate_image(apikey=os.environ["HORDE_API_KEY"], **kwargs))
    if "err" in data:
        logger.error(data)
        return jsonify(data), 400
    return jsonify(data), 200


@app.route("/caption")
def caption():
    kwargs = request.get_json()
    data = asyncio.run(caption_image(apikey=os.environ["HORDE_API_KEY"], **kwargs))
    if "err" in data:
        logger.error(data)
        return jsonify(data), 400
    return jsonify(data), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
