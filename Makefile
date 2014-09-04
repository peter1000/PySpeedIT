#!/bin/bash

PYTHON=/usr/bin/env python3

PACKAGE = PySpeedIT

.PHONY: help clean_docs clean cleanall clean_force_exclude_files tests tests_cover docs build_ext build_ext_force build_force install install_develop uninstall_develop dist pypi_all check_setup cython_annotate init_versioneer code_analysis_pylint

help:
	@echo 'Please use: `make <target>` where <target> is one of'
	@echo '  clean_docs                 removes only: `build/sphinx`'
	@echo '  clean                      clean: FILES:`.coverage, MANIFEST, *.pyc, *.pyo, *.pyd, *.o, *.orig` and DIRS: `*.__pycache__,  *.egg-info`'
	@echo '  cleanall                   clean PLUS remove: DIRS: `build, dist, cover, *._pyxbld` and FILES in MAIN_PACKAGE_PATH: `*.so, *.c` and cython annotate html'
	@echo '  clean_force_exclude_files  clean PLUS remove: any FILES in 'setup.py' `CleanCommand.exclude_files`'
	@echo '  tests                      test the project build any extensions before'
	@echo '  tests_cover                test with coverage report: dir cover:: with cython extensions before'
	@echo '  docs                       build the docs for the project'
	@echo '  build_ext                  compile any extension modules if needed: using timestamps'
	@echo '  build_ext_force            force re-generation of all cython .c files and compile all extensions'
	@echo '  build_force                build the project: force re-generation of all cython .c files and compile all extension'
	@echo '  install                    force re-compile and install the package'
	@echo '  install_develop            install the package in:development-mode'
	@echo '  uninstall_develop          uninstall the package: development-mode'
	@echo '  dist                       force re-compile and build a source distribution tar file'
	@echo '  pypi_all                   force re-compile and re-register/upload (inclusive docs) to pypi'
	@echo '  check_setup                checks the setup.py file'
	@echo '  cython_annotate            Cython’s code analysis'
	@echo '  init_versioneer            inti versioneer for the project'
	@echo '  code_analysis_pylint       pylint the project: ends always with an makefile error?'

clean_docs:
	${PYTHON} setup.py clean --onlydocs
	@echo -e '\n=== finished clean_docs'

clean:
	${PYTHON} setup.py clean
	@echo -e '\n=== finished clean'

cleanall:
	${PYTHON} setup.py clean --all
	@echo -e '\n=== finished cleanall'

clean_force_exclude_files:
	${PYTHON} setup.py clean --excludefiles
	@echo -e '\n=== finished clean_force_exclude_files'

tests:
	${PYTHON} setup.py clean
	${PYTHON} setup.py cython --timestamps
	${PYTHON} setup.py build_ext --inplace
	${PYTHON} setup.py clean
	${PYTHON} setup.py nosetests
	${PYTHON} setup.py clean
	@echo -e '\n=== finished tests'

tests_cover:
	${PYTHON} setup.py clean
	${PYTHON} setup.py cython --timestamps
	${PYTHON} setup.py build_ext --inplace
	${PYTHON} setup.py clean
	${PYTHON} setup.py nosetests --cover-branches --with-coverage --cover-html --cover-erase --cover-package=PySpeedIT
	${PYTHON} setup.py clean
	@echo -e '\n=== finished tests_cover'

docs:
	${PYTHON} setup.py clean --onlydocs
	${PYTHON} setup.py build_sphinx -E
	${PYTHON} setup.py clean
	@echo -e '\n=== finished docs'

build_ext:
	${PYTHON} setup.py clean
	${PYTHON} setup.py cython --timestamps
	${PYTHON} setup.py build_ext --inplace
	${PYTHON} setup.py clean
	@echo -e '\n=== finished build_ext'

build_ext_force:
	${PYTHON} setup.py clean --all
	${PYTHON} setup.py cython
	${PYTHON} setup.py build_ext --inplace --force
	${PYTHON} setup.py clean
	@echo -e '\n=== finished build_ext_force'

build_force:
	${PYTHON} setup.py clean --all
	${PYTHON} setup.py cython
	${PYTHON} setup.py build_ext --inplace --force
	${PYTHON} setup.py build --force
	${PYTHON} setup.py clean
	@echo -e '\n=== finished build_force'

install:
	${PYTHON} setup.py clean --all
	${PYTHON} setup.py cython
	${PYTHON} setup.py build_ext --inplace --force
	${PYTHON} setup.py build --force
	${PYTHON} setup.py install
	${PYTHON} setup.py clean
	@echo -e '\n=== finished install'

install_develop:
	${PYTHON} setup.py clean --all
	${PYTHON} setup.py cython
	${PYTHON} setup.py build_ext --inplace --force
	${PYTHON} setup.py develop --exclude-scripts
	${PYTHON} setup.py clean
	@echo -e '\n=== finished install_develop'

uninstall_develop:
	${PYTHON} setup.py develop --uninstall
	${PYTHON} setup.py clean
	@echo -e '\n=== finished uninstall_develop'

dist:
# just to make sure it compiles
	${PYTHON} setup.py clean --all
	${PYTHON} setup.py cython
	${PYTHON} setup.py build_ext --inplace --force
# do it
	${PYTHON} setup.py clean --all
	${PYTHON} setup.py cython
	${PYTHON} setup.py sdist
	${PYTHON} setup.py clean
	@echo -e '\n=== finished dist'

pypi_all:
# just to make sure it compiles
	${PYTHON} setup.py clean --all
	${PYTHON} setup.py cython
	${PYTHON} setup.py build_ext --inplace --force
# do it
	${PYTHON} setup.py clean --all
	${PYTHON} setup.py cython
	${PYTHON} setup.py check
	${PYTHON} setup.py register
	${PYTHON} setup.py sdist upload
	${PYTHON} setup.py build_sphinx upload_docs
	${PYTHON} setup.py clean
	@echo -e '\n=== finished pypi_all'

check_setup:
	${PYTHON} setup.py clean
	${PYTHON} setup.py check
	${PYTHON} setup.py clean
	@echo -e '\n=== finished check_setup'

cython_annotate:
	${PYTHON} setup.py cython --annotate
	@echo -e '\n=== finished cython_annotate'

init_versioneer:
	${PYTHON} setup.py versioneer
	@echo -e '\n=== finished init_versioneer'

code_analysis_pylint:
	pylint -f colorized PySpeedIT
	@echo -e '\n=== finished code_analysis_pylint'
