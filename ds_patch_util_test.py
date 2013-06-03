#!/usr/bin/python
#coding=utf-8
import os
import sys
import subprocess
import argparse
from ds_test import *

parser = argparse.ArgumentParser()
parser.add_argument('-all', '--print-all', default= False, action = 'store_true', dest='all', help = 'print all damaged packages')
parser.add_argument('-u', '--print-unmet', default= False, action = 'store_true',dest='u', help = 'print packages with unmets')
parser.add_argument('-p', default= False, action = 'store_true', dest='p', help = 'print packages with unmatched provides')
parser.add_argument('-c', '--print-conflicts', default = False, action = 'store_true',dest='c', help = 'print packages with unmatched conflicts')
parser.add_argument('dir_file', metavar='DIRECTORY_FILE')
parser.add_argument('index_files_directories', metavar='INDEX_FILES_PATH', nargs='+')
args = parser.parse_args()

index_parser = IndexParser()

index_files = []
for dir in args.index_files_directories:
	index_files.append(index_parser._append_index_filename(dir))

all_index_pkgs_list = list(index_parser.get_packages_from_index_files(index_files))

tester = IndexTester(args.dir_file)
test_result = tester.test_index(all_index_pkgs_list)
print test_result
directories = args.index_files_directories
dir_string = ""

for cur_dir_number in range(0, len(directories)):
	for dir_number in range(0, len(directories)):
		if dir_number != cur_dir_number:
			dir_string += directories[dir_number] + ":"

	current_file = index_parser._append_index_filename(directories[cur_dir_number])
	packages_list = list(index_parser.get_packages_from_index_file(current_file))
	for package_num in xrange(0, len(packages_list), 1000):
		subprocess.call(["ds-patch", directories[cur_dir_number], "--del", packages_list[package_num].name],stdout=open("logfile.txt", "w"))
		print "after deleting ", packages_list[package_num].name
		if 9 == ((package_num / 1000) % 10):
			subprocess.call(["ds-provides", "-s", dir_string[:-1], directories[cur_dir_number]],stdout=open("logfile.txt", "w"))
		all_index_pkgs_list = list(index_parser.get_packages_from_index_files(index_files))
		tester.add_unmets_to_ignore(packages_list[package_num])
		new_test_result = tester.test_index(all_index_pkgs_list)
		result_diff = new_test_result.diff(test_result)
		test_result = new_test_result
		print result_diff
		if args.all:
			test_result.print_damages(DAMAGE_TYPE_UNMATCHED_REQUIRE)
			test_result.print_damages(DAMAGE_TYPE_UNMATCHED_PROVIDE)
			test_result.print_damages(DAMAGE_TYPE_UNMATCHED_CONFLICT)
		if args.u:
			test_result.print_damages(DAMAGE_TYPE_UNMATCHED_REQUIRE)
		if args.p:
			test_result.print_damages(DAMAGE_TYPE_UNMATCHED_PROVIDE)
		if args.c:
			test_result.print_damages(DAMAGE_TYPE_UNMATCHED_CONFLICT)