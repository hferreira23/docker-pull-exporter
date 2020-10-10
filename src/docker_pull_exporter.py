#!/usr/bin/env python3
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from prometheus_client import make_wsgi_app
import requests
import copy
import string
import random
import logging
import yaml

#Logging
logger = logging.getLogger(__name__)

#Create WSGI app
metrics_app = make_wsgi_app(REGISTRY)

#Get Docker Pull metrics
class CustomCollector(object):
    def __init__(self):
        pass

    def collect(self):
        #Read containers from yml
        with open('containers.yml') as f:
            data = yaml.safe_load(f)
            containers = data['containers']

            #Replace invalid chars for prometheus metrics
            #bad_chars = ["-", "."]
            delete_dict = {sp_character: '_' for sp_character in string.punctuation}
            table = str.maketrans(delete_dict)

            #Fetch metrics
            response_json = []
            for k, v in containers.items():
                url = "https://hub.docker.com/v2/repositories/"+v.get('namespace')+"/"+v.get('name')+"/"
                response = requests.get(url)
                response_json.append(copy.deepcopy(response.json()))

            #Generate metric output
            for item in response_json:
                docker_namespace = item['namespace']
                docker_name = item['name']
                docker_namespace = docker_namespace.translate(table)
                docker_name = docker_name.translate(table)
                g = GaugeMetricFamily('dockerpulls_'+docker_namespace+'_'+docker_name+'_total', 'Total Pulls for: '+item['namespace']+'/'+item['name'])
                g.add_metric('docker_pulls', item['pull_count'])
                yield g

#Register the collector for metrics display
REGISTRY.register(CustomCollector())

#Sets the /metrics
#/ has a welcoming message
def docker_pull(environ, start_fn):
    if environ['PATH_INFO'] == '/metrics':
        return metrics_app(environ, start_fn)
    start_fn('200 OK', [])
    return [b'Hi there \\o\n\nMaybe you wanna go to /metrics!? :)']
