#!/usr/bin/env /usr/bin/python

'''

This script is a simple tool to automate getting and setting of KUMO cross points via python
On get success, the script returns the source 
On set success, the script returns the source and destination separated by a comma
On failure, the script returns an error code
-1: can't connect to KUMO (check your URL)
-2: destination out of range (not enough destinations in router)
-3: source is out of range (not enough sources in router)
Requires installation of Requests module, can be installed with 'pip install requests'

'''

import requests
import argparse
import json

parser = argparse.ArgumentParser(description='Set and Get AJA KUMO cross points.  On get success, the script returns the source.  On set success, the script returns the source and destination separated by a comma.  On failure, the script returns -1')
parser.add_argument('-d','--get_xpt',dest='dest',metavar="CROSSPOINT",type=int,nargs=1,help="Get crosspoint source for destination")
parser.add_argument('-s','--set_xpt',dest='source',metavar="CROSSPOINT",type=int,nargs=1,help="Set crosspoint source for destination (defined by -d)")
parser.add_argument('-a','--address',dest='kumo',metavar="ADDRESS",type=str,nargs=1,help="IP address or DNS name of KUMO")
parser.add_argument('-e','--print_error',dest='err',action='store_true',default=False,help="Print out all error codes and exit")
args = parser.parse_args()

def printError():
	print "Error Codes:"
	print ""
	print "-1: can't connect to KUMO (check your URL or network)"
	print "-2: destination out of range (not enough destinations in router)"
	print "-3: source is out of range (not enough sources in router)"
	print ""	
	exit()

if args.err is True:
	printError()

if args.dest is None:
	print "No destination defined, exiting."
	exit()

if args.kumo is None:
	print "No router defined, exiting."
	exit()

#set our kumo URL
kumo = 'http://' + args.kumo[0] + '/options'

#get kumo source count (sc)
try:
	r = requests.get(kumo + '?action=get&paramid=eParamID_NumberOfSources')
except requests.ConnectionError:
	print -1
	exit()	
j = json.loads(r.text)
sc = j['value']

#get kumo destination count (dc)
try:
	r = requests.get(kumo + '?action=get&paramid=eParamID_NumberOfDestinations')
except requests.ConnectionError:
	print -1
	exit()
j = json.loads(r.text)
dc = j['value']

# if there isn't a source set on the cli, simply look up the source of the supplied destination
if not args.source:
	# if destination is larger than router size, exit with error
	if args.dest[0] > int(dc):
		print -2
		exit()	
	#try getting source for defined destination
	try:
		r = requests.get(kumo + '?action=get&paramid=eParamID_XPT_Destination' + str(args.dest[0]) + '_Status',timeout=0.2)
	except requests.ConnectionError:
		print -1
		exit()
	j = json.loads(r.text)
	#if we get an error, print it, other wise print out source	
	if j['value'] == '-1':
		print -2
	else:
		print j['value']
else:
	#if source is larger than router size, exit with error
	if args.source[0] > int(sc):
		print -3
		exit()
	# there is a source defined, so switch it
	post_data = {'paramName': 'eParamID_XPT_Destination' + str(args.dest[0]) + '_Status','newValue': str(args.source[0])}
	try:	
		r = requests.post(kumo,data=post_data,timeout=0.2)
	except requests.ConnectionError:
		print -1
		exit()
		
	j = json.loads(r.text)
	#if we have an error, just return -2, if not return source,destination
	if j['value'] == '-1':
		print -2
	else:
		print j['value'] + ',' + str(args.dest[0])


