import asyncio
import os
import traceback

from flask import Flask, jsonify, request
from loguru import logger

from horde import async_generate_image

app = Flask(__name__)


@app.route("/generate")
def generate():
    kwargs = request.get_json()
    data = asyncio.run(
        async_generate_image(apikey=os.environ["HORDE_API_KEY"], **kwargs)
    )
    if "err" in data:
        logger.error(data)
        return jsonify(data), 400
    return jsonify(data), 200


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
