#!/usr/bin/python
#coding=utf-8
import os
import sys
import argparse
import gzip


class Package:
	def __init_(self, name=None, short_name=None, provides=None, requires=None, conflicts=None):
		self.name = name
		self.short_name = short_name
		self.provides = provides
		self.requires = requires
		self.conflicts = conflicts

	def __str__(self):
		return "[%s]" % self.name

	@property
	def require_conflicts(self):
		return list(set(self.requires) | set(self.conflicts))


class IndexParser:
	def __init__(self):
		self.index_filename = 'rpms.data.gz'

	def get_packages_from_index_file(self, data_file):
		"""
		�������-������ ������� ��� �����. 
		TODO: ��������� �����?
		���������� ���������, ������ ������� �������� �������� ������������� ������
		� ���������� � ������
		TODO: ������ ����� ��� ������ ����� Package
		"""
		file = gzip.open(data_file, "rb")

		while True:
			file_line = file.readline()
			if not file_line:
				break
			current_package = Package()
			provides = []
			require = []
			conflict = []
			require_conflict = []

			while True:
				if not file_line:
					break

				if file_line.startswith('['):
					current_package.name = file_line[1:-2]
					break

				file_line = file.readline()

			while True:
				if not file_line:
					break

				if file_line.startswith('n'):
					current_package.short_name = file_line[2:]
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

				if file_line.startswith("c:"):
					conflict.append(file_line.strip()[2:])

				file_line = file.readline()

			current_package.provides = provides
			current_package.requires = require
			current_package.conflicts = conflict

			yield current_package

	def get_packages_from_index_files(self, index_files=[]):
		"""
		TODO: ��� ���������, ��� ����������?
		"""
		for file in index_files:
			for package in self.get_packages_from_index_file(file):
				yield package

	def _append_index_filename(self, dirname):
		return dirname + "/" + self.index_filename

	def get_packages_from_index_directory(self, index_dir):
		return self.get_packages_from_index_file(self._append_index_filename(index_dir))

	def get_packages_from_index_directories(self, index_dirs=[]):
		index_files = map(lambda x: self._append_index_filename(x), index_dirs)
		return self.get_packages_from_index_files(index_files)


DAMAGE_TYPE_UNMATCHED_PROVIDE = 0
DAMAGE_TYPE_UNMATCHED_CONFLICT = 1
DAMAGE_TYPE_UNMATCHED_REQUIRE = 2

DAMAGE_TYPES = (DAMAGE_TYPE_UNMATCHED_PROVIDE, DAMAGE_TYPE_UNMATCHED_CONFLICT, DAMAGE_TYPE_UNMATCHED_REQUIRE)

DAMAGE_TYPES_COUNT = 3


class IndexTestResult:
	def __init__(self, packages):
		self.packages = packages
		self.damages_by_type = [set() for i in xrange(DAMAGE_TYPES_COUNT)]
		self.damages_by_type_and_packages = [dict() for i in xrange(DAMAGE_TYPES_COUNT)]

	@property
	def packages_count(self):
		return len(self.packages)

	def add_damage(self, pkg, damage, type):
		pkg = pkg.name
		self.damages_by_type[type].add(damage)
		if pkg not in self.damages_by_type_and_packages[type].keys():
			self.damages_by_type_and_packages[type][pkg] = set()

		self.damages_by_type_and_packages[type][pkg].add(pkg)

	def add_unmatched_provide(self, pkg, damage):
		self.add_damage(pkg, damage, DAMAGE_TYPE_UNMATCHED_PROVIDE)

	def add_unmatched_conflict(self, pkg, damage):
		self.add_damage(pkg, damage, DAMAGE_TYPE_UNMATCHED_CONFLICT)

	def add_unmatched_require(self, pkg, damage):
		self.add_damage(pkg, damage, DAMAGE_TYPE_UNMATCHED_REQUIRE)

	def damaged_packages_count_by_type(self, type):
		return len(self.damages_by_type_and_packages[type])

	@property
	def damaged_packages_count(self):
		return len(reduce(lambda res, x: res | x, map(lambda x: set(x), self.damages_by_type_and_packages)))

	def diff(self, other):
		result = IndexTestResult(list(set(self.packages).intersection(set(other.packages))))

		for type in DAMAGE_TYPES:
			result.damages_by_type[type] = self.damages_by_type[type] - other.damages_by_type[type]
			for pkg in self.damages_by_type_and_packages[type].keys():
				if pkg not in other.damages_by_type_and_packages[type].keys():
					result.damages_by_type_and_packages[type][pkg] = self.damages_by_type_and_packages[type][pkg]
				else:
					result.damages_by_type_and_packages[type][pkg] = self.damages_by_type_and_packages[type][pkg] - other.damages_by_type_and_packages[type][pkg]
					if len(result.damages_by_type_and_packages[type][pkg]) == 0:
						del result.damages_by_type_and_packages[type][pkg]

		return result


	def __str__(self):
		return """Found %d packages"
%d packages is damaged
%d packages have unmatched provides
%d packages have unmatched requires
%d packages have unmatched conflicts""" % (
		self.packages_count,
		self.damaged_packages_count,
		self.damaged_packages_count_by_type(DAMAGE_TYPE_UNMATCHED_PROVIDE),
		self.damaged_packages_count_by_type(DAMAGE_TYPE_UNMATCHED_REQUIRE),
		self.damaged_packages_count_by_type(DAMAGE_TYPE_UNMATCHED_CONFLICT)
		)

	def print_damages(self, type):
		if type == DAMAGE_TYPE_UNMATCHED_REQUIRE:
			type_str = "require"
		if type == DAMAGE_TYPE_UNMATCHED_PROVIDE:
			type_str = "provide"
		if type == DAMAGE_TYPE_UNMATCHED_CONFLICT:
			type_str = "conflict"
		if self.damages_by_type[type]:
			for pkg in self.damages_by_type_and_packages[type]:
				print "package %s has unmatched %s " % (pkg, type_str), ",".join(self.damages_by_type_and_packages[type][pkg])

class IndexTester:
	def __init__(self, provides_dir_file):
		self.provides_dir_file = provides_dir_file
		self.unmet_ignore_list = []

	@property
	def provides_dirs(self):
		return open(self.provides_dir_file).readline().split(':')

	def add_unmets_to_ignore(self, del_pkg):
		self.unmet_ignore_list += del_pkg.provides
		self.unmet_ignore_list.append(del_pkg.short_name)

	def test_index(self, packages):
		"""
		TODO: �� �� �����
		"""
		provides_dirs = self.provides_dirs

		provides_set = set()
		require_conflict_set = set()
		names_set = set()

		for package in packages:
			names_set.add(package.short_name)

			provides_set.update(set(package.provides))
			require_conflict_set.update(set(package.require_conflicts))

		result = IndexTestResult(packages)

		for package in packages:

			for provide in package.provides:
				for dir in provides_dirs:
					in_dir = dir in provide
					if in_dir:
						break
				if (provide not in require_conflict_set) and (not in_dir):
					result.add_unmatched_provide(package, provide)

			for r in package.requires:
				if (r not in provides_set) and (r not in names_set) and (r not in self.unmet_ignore_list):
					result.add_unmatched_require(package, r)

			for c in package.conflicts:
				if (c not in provides_set) and (c not in names_set):
					result.add_unmatched_conflict(package, c)

		return result
