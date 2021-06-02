import os
import json
import redis
from flask import Flask, request
import configparser as cp
import requests
import logging
import aiohttp
import asyncio
import time

from r2r_offer_utils.logging import setup_logger


service_name = os.path.splitext(os.path.basename(__file__))[0]
app = Flask(service_name)

# config
config = cp.ConfigParser()
config.read(f'{service_name}.conf')

# cache
cache = redis.Redis(host=config.get('cache', 'host'),
                    port=config.get('cache', 'port'),
                    decode_responses=True)


# init logging
logger, ch = setup_logger()
logger.setLevel(logging.INFO)


async def call_fc_service(session, service_name, request_id):
    
    logger.info(f'Sending request to {service_name}...')
    try:
        async with session.request(method='POST',
                                   url = f'http://{service_name}:5000/compute',
                                   json = {'request_id': request_id},
                                   headers = {'Content-Type': 'application/json'}) as response:
                json_response = await response.json()
                logger.info(f'Received response from {service_name}.')
                return json_response
    except:
        logger.info(f'Something went wrong in {service_name}.')
        response = app.response_class(
        response=f'{{"request_id": "{request_id}"}}',
        status=500,
        mimetype='application/json')
        return response
        
        
async def send_requests(request_id):
    
    logger.info('Handling asynchronous requests.')
    
    service_names = ['time-fc', 'weather-fc']
    async with aiohttp.ClientSession() as session:
        tasks = []
        for sn in service_names:
            tasks.append(asyncio.ensure_future(call_fc_service(session, sn, request_id)))
        
        await asyncio.gather(*tasks)
    logger.info('All requests have been handled.')
        
      
        
@app.route('/compute', methods=['POST'])
def handle_request():
    
    # receive the TRIAS request data
    request.get_data()
    trias_data = request.data
    
    # send the TRIAS to the trias-extractor
    logger.info('Sending POST request to trias-extractor...')
    trias_extractor_response = requests.post(url = 'http://trias-extractor:5000/extract',
                                   data = trias_data, #{"request_id": "#31:4265-#24:10239"},
                                   headers={'Content-Type': 'application/xml'}).json()
    logger.info('Received response from trias-extractor.')
    request_id = str(trias_extractor_response['request_id'])
    
    """
    # synchronous version
    logger.info('Sending POST request to time-fc...')
    time_fc_response = requests.post(url = 'http://time-fc:5000/compute',
                                     json = {'request_id': "#31:4265-#24:10239"},
                                     headers={'Content-Type': 'application/json'}).json()
    logger.info('Received response from time-fc.')
    
    logger.info('Sending POST request to weather-fc...')
    weather_fc_response = requests.post(url = 'http://weather-fc:5000/compute',
                                        json = {'request_id': "#31:4265-#24:10239"},
                                        headers={'Content-Type': 'application/json'})
    logger.info('Received response from weather-fc.')
    """
    
    # asyncrhronous version
    t0 = time.time()
    asyncio.run(send_requests(request_id))
    t1 = time.time()
    logger.info(f'Done in {t1-t0} seconds.')
    
    response = app.response_class(
        response=f'{{"request_id": {request_id}}}',
        status=200,
        mimetype='application/json'
    )
    return response
    
    
if __name__ == '__main__':
    
    FLASK_PORT = 5000
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379

    os.environ["FLASK_ENV"] = "development"

    cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)
    #print(cache.keys())

    app.run(port=FLASK_PORT, debug=True)