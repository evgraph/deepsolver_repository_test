#!/usr/bin/python
#coding=utf-8
import os
import sys
import subprocess
import argparse
from ds_test import *

parser = argparse.ArgumentParser()
parser.add_argument('index_files_directories', metavar='INDEX_FILES_PATH', nargs='+')
parser.add_argument('dir_file')
args = parser.parse_args()

index_parser = IndexParser()

index_files = [] ##������ � ������� "rpms.data.gz", ���������� �� 'index_files_directory', ��� ������� ����� test_index
for dir in args.index_files_directories:
	index_files.append(index_parser._append_index_filename(dir))

all_index_pkgs_list = list(index_parser.get_packages_from_index_files(index_files))

tester = IndexTester(args.dir_file)
test_result = tester.test_index(all_index_pkgs_list) # �������� ������ ����c� IndexTestResult
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
		##subprocess.call(["ds-patch", directories[cur_dir_number], "--del", packages_list[package_num].name],stdout=open("logfile.txt", "w"))
		##if 9 == ((package_num / 1000) % 10):
			##subprocess.call(["ds-provides", "-s", dir_string[:-1], directories[cur_dir_number]],stdout=open("logfile.txt", "w"))
		##all_index_pkgs_list = list(index_parser.get_packages_from_index_files(index_files))
		##new_test_result = tester.test_index(all_index_pkgs_list)
		##result_diff = new_test_result.diff(test_result)
		##test_result = new_test_result
		##print result_diff
		##result_diff.print_damages(DAMAGE_TYPE_UNMATCHED_REQUIRE)
