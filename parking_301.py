#!/usr/bin/env python

import open311SNSL
import json


"""
Script calls NYC 301 API and outputs json file with current 
parking information in html format.

"""

def get_301_info(service_id):
	API_id        = 'c7cf0d5b'
	API_key       = '837d0a2e46583a1e1522e73d173bbd03'
	serviceObject = open311SNSL.service(API_id, API_key, service_id)
	serviceInfo   = serviceObject.getService(serviceObject.json) 
	return serviceInfo.json()

def get_parking_status():
	service_id    = '20090318-F1C125E2-13C9-11DE-9740-D9EDAE6364CF'
	return get_301_info(service_id)


def write_parking_status_json():
	# output json filename
	out_file = 'parking.json'
	# get current parking information
	p = get_parking_status()
	# extract html description
	parking_html = p[0]['description_html']
	# write description to json file
	with open(out_file, 'wb') as f_out:
		f_out.write(json.dumps(parking_html)+'\n')



