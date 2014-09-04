""" tests all modules for syntax correctness and internal imports
"""
from glob import glob
from importlib.machinery import (
   ExtensionFileLoader,
   SourceFileLoader,
)
from inspect import (
   getfile as inspect_getfile,
   currentframe as inspect_currentframe,
)
from os import (
   walk,
   remove as os_remove,
)
from os.path import (
   abspath as path_abspath,
   basename as path_basename,
   dirname as path_dirname,
   exists as path_exists,
   join as path_join,
   splitext as path_splitext,
)
from shutil import rmtree
from sys import path as sys_path


SCRIPT_PATH = path_dirname(path_abspath(inspect_getfile(inspect_currentframe())))
PROJECT_ROOT = path_dirname(SCRIPT_PATH)

ROOT_PACKAGE_NAME = 'PySpeedIT'
ROOT_PACKAGE_PATH = path_join(PROJECT_ROOT, ROOT_PACKAGE_NAME)

sys_path.insert(0, PROJECT_ROOT)

from PySpeedIT.utils import build_cython_extension


def test_all_imports_py():
   """ Tests: test_all_imports_py: for syntax correctness and internal imports
   """
   print('::: TEST: test_all_imports_py()')
   all_modules_path = []
   for root, dirnames, filenames in walk(ROOT_PACKAGE_PATH):
      all_modules_path.extend(glob(root + '/*.py'))
   for py_module_file_path in all_modules_path:
      module_filename = path_basename(py_module_file_path)
      module_filename_no_ext = path_splitext(module_filename)[0]

      py_loader = SourceFileLoader(module_filename_no_ext, py_module_file_path)
      py_loader.load_module(module_filename_no_ext)


def test_all_imports_pyx():
   """ Tests: test_all_imports_pyx: for rebuild, syntax correctness and internal imports
   """
   print('::: TEST: test_all_imports_pyx()')
   remove_files = []
   remove_dirs = []
   all_modules_path = []
   for root, dirnames, filenames in walk(ROOT_PACKAGE_PATH):
      all_modules_path.extend(glob(root + '/*.pyx'))
   for pyx_module_file_path in all_modules_path:
      module_filename = path_basename(pyx_module_file_path)
      module_filename_no_ext = path_splitext(module_filename)[0]

      cython_extension_module_path, cython_module_c_file_path, cython_build_dir_path = build_cython_extension(
         pyx_module_file_path,
         cython_force_rebuild=True
      )

      so_loader = ExtensionFileLoader(module_filename_no_ext, cython_extension_module_path)
      so_loader.load_module(module_filename_no_ext)
      # add for cleanup
      remove_files.append(cython_module_c_file_path)
      remove_dirs.append(cython_build_dir_path)

   # Cleanup
   try:
      for file_ in remove_files:
         if path_exists(file_):
            os_remove(file_)
      for dir_ in remove_dirs:
         if path_exists(dir_):
            rmtree(dir_)
   except Exception as err:
      raise Exception('test_all_imports_pyx', 'Could not cython_clean_up: Exception: <{}>'.format(err))


def test_all_py_to_cython_compiled():
   """ Tests: test_all_py_to_cython_compiled: for syntax correctness and internal imports: all .py files compiled with
   cython: except '__init__'
   """
   print('::: TEST: test_all_py_to_cython_compiled()')
   remove_files = []
   remove_dirs = []

   all_modules_path = []
   for root, dirnames, filenames in walk(ROOT_PACKAGE_PATH):
      all_modules_path.extend(glob(root + '/*.py'))
   for py_module_file_path in all_modules_path:
      module_filename = path_basename(py_module_file_path)
      module_filename_no_ext = path_splitext(module_filename)[0]
      if '__init__' in module_filename:
         continue

      cython_extension_module_path, cython_module_c_file_path, cython_build_dir_path = build_cython_extension(
         py_module_file_path,
         cython_force_rebuild=True
      )

      # noinspection PyUnusedLocal
      so_loader = ExtensionFileLoader(module_filename_no_ext, cython_extension_module_path)

      # sometimes (if a extension module is build previously) the loading does not work with 'nose tests'
      # so_loader.load_module(module_filename_no_ext)

      # add for cleanup : inclusive the .so extension file
      remove_files.extend([cython_module_c_file_path, cython_extension_module_path])
      remove_dirs.append(cython_build_dir_path)

   # Cleanup
   try:
      for file_ in remove_files:
         if path_exists(file_):
            os_remove(file_)
      for dir_ in remove_dirs:
         if path_exists(dir_):
            rmtree(dir_)
   except Exception as err:
      raise Exception('test_all_py_to_cython_compiled', 'Could not cython_clean_up: Exception: <{}>'.format(err))


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
if __name__ == '__main__':
   test_all_imports_py()
   test_all_imports_pyx()
   test_all_py_to_cython_compiled()
