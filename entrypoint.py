# We are import the flask web framework
from flask import Flask
import json
import redis as redis
from loguru import logger
import requests
# We are define the two constants
HISTORY_ENGTH = 10
DATA_KEY = "engine_temperature"

# We are creating a Flask server, and allow us to interact with it usinfg the app variable
app = Flask(__name__)

# We are define an endpoint which accepts POST requests, and is reachable from the /record endpoint
@app.route('/record', methods=['POST'])
def record_engine_temperature():
    # every time the /record endpoint is called, the code in this blok is executed
    payload = requests.get_json(force=True)
    logger.info(f"(*) record request -- {json.dumps(payload)} (*)")
    
    engine_temperature = payload.get("engine_temperature")
    logger.info(f"engine temperature to record is: {engine_temperature}")
    
    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    
    database.lpush(DATA_KEY, engine_temperature)
    logger.info(f"stashed engine temperature in redis: {engine_temperature}")
    
    while database.llen(DATA_KEY) > HISTORY_ENGTH:
        database.rpop(DATA_KEY)
    engine_temperature_values = database.lrange(DATA_KEY, 0, -1)
    logger.info(f"engine_temperature list now contains these values: {engine_temperature_values}")
    
    logger.info(f"record request successful")
    return {"success": True}, 200
    # return a json payload, and a 200 status code to the client
    return {"success": True}, 200

# We are pratically identical to the above
@app.route('/collect', methods=['POST'])
def collect_engine_temperature():
    return {"success": True}, 200