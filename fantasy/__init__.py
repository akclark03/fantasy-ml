import logging
import sys

logging.basicConfig(
    format="%(asctime)s %(levelname)-5s [%(name)-16s]  %(message)s (%(filename)s:%(lineno)d)",
    level=logging.INFO,
    stream=sys.stdout,
)
logging.getLogger("nfl").setLevel(logging.INFO)
