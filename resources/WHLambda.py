# Creating Handler for obtaining Latency and Availability for Webresource
import urllib3
from datetime import datetime
from CloudwatchPutMetric import CloudwatchPutMetric
import constants as constants
import boto3
import os

def lambda_handler(event, context):
    # get latency and availability of the web resource
    values = dict()
    #####################################################################################################
    #                                        Get the URLs list from table                               #
    #                                   And append that list in constant file                           #
    #####################################################################################################
    
    # Get the service resource.
    dynamodb = boto3.resource('dynamodb')
    # set environment variable
    tableName = os.environ["URL_TABLE"]
    table = dynamodb.Table(tableName)

    response = table.scan()['Items']
    for i in range(len(response)):
        constants.MY_URLS_VAR.append(response[i]["url"])
        print(constants.MY_URLS_VAR)

    #####################################################################################################

    cw = CloudwatchPutMetric()

    # loop the list of url
    for url in constants.MY_URLS_VAR:
        # code for links here
        availability = getAvailability(url)
        latency = getLatency(url)
        values.update({"Availability": availability, "Latency": latency})
        print(values)

        dimension = [{'Name': 'URL','Value': url}]

        responseAvail = cw.put_data(constants.URL_MONITOR_NAMESPACE,
        constants.URL_MONITOR_NAME_AVAILABILITY,
        dimension, availability)

        responseLatency = cw.put_data(constants.URL_MONITOR_NAMESPACE,
        constants.URL_MONITOR_NAME_LATENCY,
        dimension, latency)
   
# input parameters: None
# return values: boolean 1 or 0
def getAvailability(url):
    http = urllib3.PoolManager()
    response = http.request("GET", url)
    if response.status==200:
        return 1.0
    else:
        return 0.0

# input parameters: None
# return values: latency in seconds
def getLatency(url):
    http = urllib3.PoolManager()
    start = datetime.now()
    response = http.request("GET", url)
    end = datetime.now()
    diff = end - start  #time difference
    latencySec = round(diff.microseconds * .000001, 6)
        
    return latencySec
