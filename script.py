#!/usr/bin/python
import os
import sys

import argparse

def parse_packages(data_file):
	file = open(data_file)
	while True:
		file_line = file.readline()
		if not file_line:
			break
		current_package = {}
		provides = []
		require = []
		conflict = []
		require_conflict = []
		while True:
			if not file_line:
				break
		
			if file_line.startswith('['):
				current_package['name'] = file_line[1:-2]
				break
				
			file_line = file.readline()
		
		while True:
			if not file_line:
				break
		
			if file_line.startswith('n'):
				current_package['n'] = file_line[2:]				
				break
				
			file_line = file.readline()	
		while True:		
			file_line = file_line.strip().split(' ')[0]
			if not file_line:
				break
			
			if file_line.startswith("p:"):
				provides.append(file_line.strip()[2:])
				
			if file_line.startswith("r:"):
				require.append(file_line.strip()[2:])
				require_conflict.append(file_line.strip()[2:])
					
			if file_line.startswith("c:"):
				conflict.append(file_line.strip()[2:])
				require_conflict.append(file_line.strip()[2:])
					
			file_line = file.readline()	
	
		current_package['p'] = provides
		current_package['r'] = require
		current_package['c'] = conflict
		current_package['rc'] = require_conflict
		
		yield current_package
		
def parse_package_set(args=[]):
	for file in args:
		for package in parse_packages(file):
			yield package

parser = argparse.ArgumentParser()
parser.add_argument('dir_file', metavar='DIRECTORY_FILE')
parser.add_argument('index_files', metavar='INDEX_FILE', nargs='+')
args = parser.parse_args()
	
index_files= args.index_files
directories = []
dir_file = open(args.dir_file)
directories = dir_file.readline().split(':')
packages = []
provides_set = set()
require_conflict_set = set()
names_set = set()

for package in parse_package_set(index_files):	
	names_set.add(package['n'])
	packages.append(package)
	for s in package['p']:
		provides_set.add(s)
	for s in package['rc']:
		require_conflict_set.add(s)

damaged_package_count =0
damaged_p_count = 0
damaged_r_count=0
damaged_c_count=0
for package in packages:
	is_damaged_p = False
	is_damaged_rc = False
	is_damaged_r = False
	is_damaged_c = False
	
	for provide in package['p']:		
		for dir in directories:
			in_dir = dir in provide
			if in_dir:
				break
		if (provide not in require_conflict_set) and (not in_dir):
			print package['name'], "has unmatched provide", provide 
			is_damaged_p = True
	
	for r in package['r']:
		if (r not in provides_set) and (r not in names_set):
			print package['name'], "has unmatched require", r
			is_damaged_r = True
	for c in package['c']:
		if (c not in provides_set) and (c not in names_set):
			print package['name'], "has unmatched conflict", c
			is_damaged_c = True
	if is_damaged_p or is_damaged_c or is_damaged_r:
		damaged_package_count+=1
	if is_damaged_p:
		damaged_p_count += 1
	if is_damaged_r:
		damaged_r_count += 1
	if is_damaged_c:
		damaged_c_count += 1
		
print "Found", len(packages), "packages"
print damaged_package_count, "packages is damaged"
print damaged_p_count,"packages have unmatched provides" 
print damaged_r_count, "packages have unmatched requires "
print damaged_c_count, "packages have unmatched conflicts " 

			

