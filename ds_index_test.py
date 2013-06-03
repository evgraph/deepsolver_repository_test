#!/usr/bin/python
#coding=utf-8
import os
import sys
import argparse
from ds_test import * 


parser = argparse.ArgumentParser()
parser.add_argument('-all', '--print-all', default= False, action = 'store_true', dest='all', help = 'print all damaged packages')
parser.add_argument('-u', '--print-unmet', default= False, action = 'store_true',dest='u', help = 'print packages with unmets')
parser.add_argument('-p', default= False, action = 'store_true', dest='p', help = 'print packages with unmatched provides')
parser.add_argument('-c', '--print-conflicts', default = False, action = 'store_true',dest='c', help = 'print packages with unmatched conflicts')
parser.add_argument('dir_file', metavar='DIRECTORY_FILE')## ��������� �������� dir_file - ���� � ����������, ������� �� ������� �������������, ��� ���������� provides
parser.add_argument('index_files', metavar='INDEX_FILE', nargs='+') ## ��������� �������� index_files - ���� ��� ����� ������ � ��������� ��� ��������
args = parser.parse_args()

index_parser = IndexParser()

packages = list(index_parser.get_packages_from_index_files(args.index_files))

tester = IndexTester(args.dir_file)

test_result = tester.test_index(packages)
print test_result
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