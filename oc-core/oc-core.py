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

from r2r_offer_utils.cache_operations import read_data_from_cache_wrapper
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
    
    logger.info(f'o-o-o-o-o-o-o-o Sending request to {service_name}... o-o-o-o-o-o-o-o')
    try:
        async with session.request(method='POST',
                                   url = f'http://{service_name}:5000/compute',
                                   json = {'request_id': request_id},
                                   headers = {'Content-Type': 'application/json'}) as response:
                json_response = await response.json()
                logger.info(f'o-o-o-o-o-o-o-o Received response from {service_name}. o-o-o-o-o-o-o-o')
                return json_response
    except:
        logger.info(f'X-X-X-X-X-X Something went wrong in {service_name}. X-X-X-X-X-X')
        response = app.response_class(
        response=f'{{"request_id": "{request_id}"}}',
        status=500,
        mimetype='application/json')
        return response
        
        
async def send_requests_to_fcs(request_id):
    
    logger.info('Handling asynchronous requests.')
    
    service_names = ['time-fc', 'weather-fc', 'price-fc']
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
    # call the feature collectors (synchronous version)
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
    
    # call the feature collectors (asyncrhronous version)
    t0 = time.time()
    asyncio.run(send_requests_to_fcs(request_id))
    t1 = time.time()
    logger.info(f'Done in {t1-t0} seconds.')
    
    # aggregate factors
    output_offer_level, output_tripleg_level = read_data_from_cache_wrapper(pa_cache=cache, pa_request_id=request_id,
                                                                               pa_offer_level_items=['total_price', 
                                                                                                     'ticket_coverage',
                                                                                                     'duration',
                                                                                                     'time_to_departure',
                                                                                                     'rush_overlap',
                                                                                                     'waiting_time'],
                                                                               pa_tripleg_level_items=['start_time', 'end_time'])
    
    for offer_id in output_offer_level['offer_ids']:
        logger.info('Total price: ' + str(output_offer_level[offer_id]['total_price']))
        logger.info('Ticket coverage: ' + str(output_offer_level[offer_id]['ticket_coverage']))
        logger.info('Duration: ' + str(output_offer_level[offer_id]['duration']))
        logger.info('Time to departure: ' + str(output_offer_level[offer_id]['time_to_departure']))
        logger.info('Rush hour overlap: ' + str(output_offer_level[offer_id]['rush_overlap']))
        logger.info('Waiting time: ' + str(output_offer_level[offer_id]['waiting_time']))

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