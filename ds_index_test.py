#!/usr/bin/python
#coding=utf-8
import os
import sys
import argparse
from ds_test import * 


parser = argparse.ArgumentParser() ##������� ������
parser.add_argument('dir_file', metavar='DIRECTORY_FILE')## ��������� �������� dir_file - ���� � ����������, ������� �� ������� �������������, ��� ���������� provides
parser.add_argument('index_files', metavar='INDEX_FILE', nargs='+') ## ��������� �������� index_files - ���� ��� ����� ������ � ��������� ��� ��������
args = parser.parse_args()

index_parser = IndexParser()

packages = list(index_parser.get_packages_from_index_files(args.index_files))

tester = IndexTester(args.dir_file)

test_result = tester.test_index(packages)

print test_result.diff(test_result)