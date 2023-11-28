import asyncio
import os
import traceback

from flask import Flask, jsonify, request
from loguru import logger

from horde import async_generate_image

app = Flask(__name__)


@app.route("/generate")
def generate():
    data = None
    try:
        kwargs = request.get_json()
        data = asyncio.run(
            async_generate_image(apikey=os.environ["HORDE_API_KEY"], **kwargs)
        )
        if "err" in data:
            raise Exception("There was an error.")
        return jsonify(data), 200
    except Exception as e:
        logger.error(data)
        return jsonify(data), 204


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
