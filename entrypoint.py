# We are import the flask web framework
from flask import Flask
import json
import redis as redis
from loguru import logger
import requests
# We are define the two constants
HISTORY_ENGTH = 10
DATA_KEY = "engine_temperature"
DATA_KEY1 = "current_engine_temperature"
DATA_KEY2 = "average_engine_temperature"

# We are creating a Flask server, and allow us to interact with it usinfg the app variable
app = Flask(__name__)

# We are define an endpoint which accepts POST requests, and is reachable from the /record endpoint
@app.route('/record', methods=['POST'])
def record_engine_temperature():
    # every time the /record endpoint is called, the code in this block is executed
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

# We are pratically identical to the above
@app.route('/collect', methods=['GET'])
def collect_engine_temperature():
    # every time the /record endpoint is called, the code in this block is executed
    payload = requests.get_json(force=True)
    logger.info(f"(*) collect request -- {json.dumps(payload)} (*)")
    
    database = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
    
    current_engine_temperature_values = database.lrange(DATA_KEY1, 0, HISTORY_ENGTH - 1)
    current_engine_temperature_values = list(map(float, current_engine_temperature_values))
    
    if current_engine_temperature_values:
        current_engine_temperature = current_engine_temperature_values[0]
    else:
        current_engine_temperature = None
        
    logger.info(f"Engine's current temperature to collect is: {current_engine_temperature}")

    # We are fetch average engine temperature
    average_engine_temperature_values = database.lrange(DATA_KEY2, 0, HISTORY_ENGTH - 1)
    average_engine_temperature_values = list(map(float, average_engine_temperature_values))
    
    if average_engine_temperature_values:
        average_engine_temperature = sum(average_engine_temperature_values) / len(average_engine_temperature_values)
    else:
        average_engine_temperature = None
        
    logger.info(f"Engine's average temperature to collect is: {average_engine_temperature}")
    
    logger.info("collect request successful")
    
    return{"current_engine_temperature": current_engine_temperature,
           "average_engine_temperature": average_engine_temperature},200