#!/usr/bin/env /usr/bin/python

import sys
import subprocess
import os.path
import argparse

#build menu and help file

parser = argparse.ArgumentParser(description='Compare source and destination filesystems for relative files. Make sure the user you run this script as has full access to the entire source and destination filesystems')
parser.add_argument('-s','--source_path',dest='source',metavar="PATH",type=str,nargs=1,help="Source Filesystem Path",required=True)
parser.add_argument('-d','--dest_path',dest='dest',metavar="PATH",type=str,nargs=1,help="Destination Filesystem Path",required=True)
parser.add_argument('-t','--temp_file_location',dest='tfl',metavar="PATH",type=str,nargs=1,help="Temp File Filesystem Path (default is /tmp)")
parser.add_argument('-r','--rerun',action='store_true',dest='rerun',default=False,help="Rerun against existing find")
parser.add_argument('-i','--ignore-specials',action='store_true',dest='ignore',default=False,help="Ignore .DS_Store, ._, .Spotlight, and .Trashes files/folders")
parser.add_argument('-q','--quiet-mode',action='store_true',dest='quiet',default=False,help="Do not output file list to console, only to error file")
parser.add_argument('--source_file_list',dest='source_file_list',metavar="FILE",type=str,nargs=1,help="Manually define source file list (skips find step)")
parser.add_argument('--dest_file_list',dest='dest_file_list',metavar="FILE",type=str,nargs=1,help="Manually define dest file list (skips find step)")
args = parser.parse_args()

#quick validator for user input
def validator(answer):
	if answer is "Y" or answer is "y":
		return True
	else:
		return False

#function strip trailing slash from any path variable if it exists
def path_fixer(path):
	if(path[-1:] is "/"):
		ret_path = path[:-1]
	else:
		ret_path = path
	return ret_path
	
#run find on path and create master file list
def build_file_list(fs_path,temp_path,rerun):
	new_file = temp_path + "/" + os.path.basename(fs_path) + ".list"
	if rerun is True:
		print "Rerunning with file " + new_file
	else:
		if os.path.isfile(new_file):
			go = raw_input("File " + new_file + " already exists, overwrite (Y/N)? ")
			if validator(go) is True:
				print "Overwriting " + new_file + "..."
			else:
				print "Canceling..."
				exit()
		cmd = "/usr/bin/find " + fs_path + " > " + new_file
		ps = subprocess.Popen(cmd,shell=True)
		ps.wait()					
	return new_file
			
#open file, loop, and remove heading mount points function
def path_stripper(source_file,path_to_strip):
	print "Opening " + source_file
	f = open(source_file)
	fw_name = source_file + '.strip'
	print "Creating " + fw_name
	fw = open(fw_name,'w')

	for line in f.readlines():
		if line.startswith(path_to_strip):
			newline = line[len(path_to_strip):]
			fw.write(newline)
	return fw_name

#function to check compare file and build error file

#validate that our important inputs are valid
err = 0
if not args.source:
	print "No Source Defined"
	err = err +1
if not args.dest:
	print "No Destination Defined"
	err = err +1
if err is not 0:
	print "Errors found, exiting"
	parser.print_help()
	exit()

#make sure our paths don't have trailing slashes
source = path_fixer(args.source[0])
dest = path_fixer(args.dest[0])

#make sure our source/destination are actually there
if not os.path.isdir(source):
	go = raw_input("Path " + source + " does not appear to be mounted.  This will cause all unique files to show in missing log as they cannot be checked for existence.  Do you want to contine (Y/N)? ")
	if validator(go) is not True:
		print "Canceling on user input."
		exit()
	else:
		if args.source_file_list is None:
			print "Can't continue, no source file list provided"
			exit()						
		else:
			if not os.path.isfile(args.source_file_list[0]):
				print "Could not find file " + args.source_file_list[0] + ". Exiting."
				exit()
					
if not os.path.isdir(dest):
	go = raw_input("Path " + dest + " does not appear to be mounted.  This will cause all unique files to show in missing log as they cannot be checked for existence.  Do you want to contine (Y/N)? ")
	if validator(go) is not True:
		print "Canceling on user input."
		exit()
	else:
		if args.dest_file_list is None:
			print "Can't continue, no dest file list provided"
			exit()					
		else:
			if not os.path.isfile(args.dest_file_list[0]):
				print "Could not find file " + args.dest_file_list[0] + ". Exiting."
				exit()		

#if a default temp file path isn't set, use /tmp
if args.tfl is None:
	tfl = "/tmp"
else:
	tfl = path_fixer(args.tfl[0])
	if not os.path.isdir(tfl):
		print tfl + " is not a valid temp file directory"
		err = err + 1

#if any errors happened in validation, exit
if err is not 0:
	print "Errors found, exiting"
	parser.print_help()	
	exit()

#check if source file list is called out in CLI or we have to run find, then run find if necessary
if args.source_file_list is None:	
	print "Building file list for " + source
	source_list_file = build_file_list(source,tfl,args.rerun)
else:
	print "Attempting to use " + args.source_file_list[0]
	if not os.path.isfile(args.source_file_list[0]):
		print "Source file list does not exist, exiting"
		exit()
	else:
		source_list_file = args.source_file_list[0]

#check if dest file list is called out in CLI or we have to run find, then run find if necessary
if args.dest_file_list is None:	
	print "Building file list for " + dest
	dest_list_file = build_file_list(dest,tfl,args.rerun)
else:
	print "Attempting to use " + args.dest_file_list[0]
	if not os.path.isfile(args.dest_file_list[0]):
		print "Destination file list does not exist, exiting"
		exit()
	else:
		dest_list_file = args.dest_file_list[0]

#build our strip file source
print "Building strip file for " + source
source_strip_file = path_stripper(source_list_file,source)

#build our strip file destination
print "Building strip file for " + dest
dest_strip_file = path_stripper(dest_list_file,dest)

#build our comparable file
print "Creating compare file"
compare_file = tfl + "/" + os.path.basename(source) + "-" + os.path.basename(dest) + ".compare"
c = open(compare_file,'w')

#run our compare sort.  If -i flag is called, add grep commands to limit returns
print "Comparing source and destination for unique files"
print "(if you tail -f " + compare_file + " in another shell you can watch progress)"
if args.ignore is False:
	cmd = "/usr/bin/sort " + source_strip_file + " " + dest_strip_file + " | uniq -u > " + compare_file
	print cmd
else:
	cmd = "/usr/bin/sort " + source_strip_file + " " + dest_strip_file + " | uniq -u | grep -v \"\._\" | grep -v \"\.DS_Store\" | grep -v \"\.Spotlight-V100\" | grep -v \"\.Trashes\" | grep -v \"\.fseventsd\" > " + compare_file
	print cmd
ps = subprocess.Popen(cmd,shell=True)
ps.wait()

print "Unique file list complete"
c.close()

#loop through compare file and see if files exist on destination
#if -q is called, limit output to console 
print "Checking if files exist on destination"
c = open(compare_file)
error_file = tfl + "/" + os.path.basename(source) + "-" + os.path.basename(dest) + ".error"
e = open(error_file,"w")

for line in c.readlines():
	newline = dest + line
	if not os.path.isdir(newline.rstrip()):
		if os.path.isfile(newline.rstrip()):
			if args.quiet is False:
				print "File " + newline.rstrip() + " is on destination"
		else:
			if args.quiet is False:		
				print "File " + newline.rstrip() + " does not exist at destination"
			e.write(newline)

print "Checking complete, please check " + error_file
