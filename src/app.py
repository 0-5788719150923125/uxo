import asyncio
import os
import traceback

from flask import Flask, jsonify, request
from loguru import logger

from horde import async_generate_image

app = Flask(__name__)


@app.route("/generate")
def generate():
    try:
        kwargs = request.get_json()
        data = asyncio.run(
            async_generate_image(apikey=os.environ["HORDE_API_KEY"], **kwargs)
        )
        return jsonify({"data": str(data)}), 200
    except Exception as e:
        return jsonify({"data": str(e)}), 204


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
