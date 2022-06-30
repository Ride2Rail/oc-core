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

import determinant_factors

from r2r_offer_utils.cache_operations import read_data_from_cache_wrapper, store_simple_data_to_cache_wrapper
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

TIMEOUT = float(config.get('running', 'timeout'))

# init logging
logger, ch = setup_logger()
logger.setLevel(logging.INFO)


async def call_fc_service(session, service_name, request_id):
    
    logger.info(f'o-o-o-o-o-o-o-o Sending request to {service_name}... o-o-o-o-o-o-o-o')
    try:
        async with session.request(method='POST',
                                   url=f'http://{service_name}:5000/compute',
                                   json={'request_id': request_id},
                                   headers={'Content-Type': 'application/json'}
                                   ) as response:
            json_response = await response.json()
            logger.info(f'o-o-o-o-o-o-o-o Received response from {service_name}. o-o-o-o-o-o-o-o')
            return json_response
            
    except asyncio.CancelledError:
        logger.info(f'O-o-O-o-O-o-O A timeout occurred in {service_name}. O-o-O-o-O-o-O')
        response = app.response_class(response=f'{{"request_id": "{request_id}"}}',
                                      status=504,
                                      mimetype='application/json'
                                      )
        return response
    except Exception:
        logger.info(f'X-X-X-X-X-X Something went wrong in {service_name}. X-X-X-X-X-X')
        response = app.response_class(response=f'{{"request_id": "{request_id}"}}',
                                      status=500,
                                      mimetype='application/json'
                                      )
        return response


async def send_requests_to_fcs(request_id):
    
    logger.info('Handling asynchronous requests to feature-collectors.')
    
    service_names = [
                     'time-fc', 
                     'weather-fc', 
                     'price-fc', 
                     'traffic-fc', 
                     'environmental-fc', 
                     'position-fc',
                     'active-fc',
                     'tsp-fc',
                     'panoramic-fc'
                    ]
    async with aiohttp.ClientSession() as session:
        tasks = []
        for sn in service_names:
            tasks.append(asyncio.ensure_future(call_fc_service(session, sn, request_id)))
        try:
            await asyncio.wait_for(asyncio.gather(*tasks), timeout=TIMEOUT)
        except asyncio.TimeoutError:
            for t in tasks:
                t.cancel()
            logger.info(f'O-o-O-o-O-o-O Timeout (after {TIMEOUT} seconds) O-o-O-o-O-o-O')
            return
    
    logger.info('All requests to feature-collectors have been handled.')
        
        
@app.route('/<request_id>', methods=['GET'])
def handle_request(request_id):

    logger.info(f'Determinant factors: {determinant_factors.determinant_factors}')

    # call the feature collectors
    t0 = time.time()
    asyncio.run(send_requests_to_fcs(request_id))
    t1 = time.time()
    logger.info(f'Feature-collectors done in {t1-t0} seconds.')
    
    # compute category scores
    output_offer_level, output_tripleg_level = read_data_from_cache_wrapper(
        pa_cache=cache,
        pa_request_id=request_id,
        pa_offer_level_items=determinant_factors.determinant_factors,
        pa_tripleg_level_items=[]
        )

    category_scores = {}
    for offer_id in output_offer_level['offer_ids']:
        category_scores[offer_id] = {}
        for cat in determinant_factors.categories:
            n_factors = len(determinant_factors.categories[cat])
            category_score = 0
            rod_index = 0
            for fact in determinant_factors.categories[cat]:
                original_factor_score = output_offer_level[offer_id][fact]
                if original_factor_score:
                    try:
                        original_factor_score = float(original_factor_score)
                    except ValueError:
                        continue
                    factor_importance = determinant_factors.rod_weights[n_factors][rod_index]
                    factor_score = original_factor_score * factor_importance
                    category_score += factor_score
                    rod_index += 1
                                        
            category_scores[offer_id][cat] = category_score

    # store 'category_scores' into the cache
    pipe = cache.pipeline()
    for offer_id in category_scores:
        temp_key = "{}:{}:{}".format(request_id, offer_id, 'categories')
        pipe.hmset(temp_key, category_scores[offer_id])
    pipe.execute()
    
    return category_scores
    
    
if __name__ == '__main__':
    
    FLASK_PORT = 5000
    REDIS_HOST = 'localhost'
    REDIS_PORT = 6379

    os.environ["FLASK_ENV"] = "development"

    cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT)

    app.run(port=FLASK_PORT, debug=True)