# Offer Categorizer Core (under development)

## Overview

The oc-core is the module of the **Ride2Rail Offer Categorizer** that is in charge of the management of the whole workflow. In particular, its responsibilities include setting up the connections between the TRIAS extractor and the feature collectors, combining their input and output, aggregate the determinant factors for each category, carry out the categorization of the offers and handling the errors that might occur at any point in the computation. 

From a general perspective, the steps performed by the OC core can be summarized as follows: 
1. A TRIAS request is sent to the OC core; 
2. The OC core sends the TRIAS data to the “trias-extractor” module, which writes the extracted data into the cache and returns the request id to the OC core;
3. The OC core sends a request to all feature collectors, attaching the request id; 
4. When all feature collectors respond, the OC core aggregates the determinant factors for each category. 
5. The OC core assigns labels to offers and writes the data into the cache. 

Requests are carried out through HTTP protocol, via POST. It is noteworthy that, in step 3, the requests are sent to the different feature collectors in an asynchronous fashion, so as to limit the overall latency to the computation time of the slowest feature collector.

## Usage

To be able to run the application, you first need to:
- upload the TRIAS files into the ``trias-extractor/trias`` folder (you can find the TRIAS files in the following repository: https://github.com/Ride2Rail/trias-xml-examples).
- run the load.sh script in ``trias-extractor``.

For all details on the trias-extractor module, please see https://github.com/Ride2Rail/trias-extractor.

### Local development (debug on)

The oc-core service should be launched as a docker container together with the Redis cache, the trias-extractor and the feature collectors. To do so, run the following command:

```bash
docker-compose up
```

### Example request

```bash
curl --header 'Content-Type: application/xml' \
     --request POST \
     --data-binary '@trias-extractor/trias/r2r_example_1.xml' \
     http://localhost:5000/compute
```
