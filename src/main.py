import asyncio
import os

from horde import async_simple_generate_example


def main():
    apikey = os.environ["HORDE_API_KEY"]
    asyncio.run(async_simple_generate_example(apikey))


if __name__ == "__main__":
    main()
