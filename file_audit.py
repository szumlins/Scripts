#!/usr/bin/env /usr/bin/python	

import os
import sys
import subprocess
import argparse
import time

parser = argparse.ArgumentParser(description='Run a short audit on filesystem path and export a CSV for analysis')
parser.add_argument('-p','--path',dest='path',metavar="PATH",type=str,nargs=1,help="Source filesystem path to scan",required=True)
parser.add_argument('-o','--out',dest='output',metavar="FILE",type=str,nargs=1,help="Location of output csv file",required=True)
args = parser.parse_args()

#function strip trailing slash from any path variable if it exists
def path_fixer(path):
	if(path[-1:] is "/"):
		ret_path = path[:-1]
	else:
		ret_path = path
	return ret_path

#validate that our source is actually a source
if os.path.isdir(args.path[0]):
	path = path_fixer(args.path[0])
else:
	print "Could not find path " + args.path[0]
	exit()

path = os.path.abspath(path)
list_file_path = "/tmp/" + os.path.basename(path) + ".list"	

with open(list_file_path, 'wb') as list_file:
	for root,subdirs,files in os.walk(path):
			#for subdir in subdirs:
			#	print subdir
			for filename in files:
				file_path = os.path.join(root, filename)
				#print file_path
				if not ".DS_Store" in file_path:
					if not file_path.startswith('.'):
						list_file.write(file_path + '\n')
				
c = open(list_file_path)
s = []
with open(os.path.abspath(args.output[0]),'wb') as csv:
	csv.write('Filename,Full Path,File Size (bytes),File Size,Creation Date\n')
	for line in c.readlines():
		if not os.path.islink(line.rstrip('\n')):
			try:
				file_size = os.path.getsize(line)
			except:
				file_size = os.path.getsize(line.rstrip('\n'))
			s.append(file_size)
			file_size_mb = file_size / 1024 / 1024 
			file_time = time.ctime(os.path.getctime(line.rstrip('\n')))
			csv.write(os.path.basename(line).rstrip('\n') + ',' + line.rstrip('\n') + ',' + str(file_size) + ',' + str(file_size_mb) + 'MB,' + file_time + '\n')
	csv.write ('total,total,' + str(sum(s)) + ',' + str(round((float(sum(s)) / 1024 / 1024 / 1024),2)) + 'GB,total\n')