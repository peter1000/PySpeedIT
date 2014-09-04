"""
===============
PySpeedIT.utils
===============

Overview
========
This module defines a couple of helpers.


Classes
=========
.. autoclass:: Err


Functions
=========
.. autofunction:: build_cython_extension

.. autofunction:: format_time
"""
from distutils.dist import Distribution
from distutils.errors import DistutilsArgError
from distutils.extension import Extension
from os.path import (
   basename as path_basename,
   dirname as path_dirname,
   splitext as path_splitext,
   join as path_join,
)

from Cython.Distutils import build_ext as cython_build_ext

from PySpeedIT import TESTED_HOST_OS


class Err(Exception):
   """Prints an own raised Project Error

   :param error_type: (str) to specify mostly from which part the error comes: e.g. CONFIG
   :param info: (list) list of strings (text info) to print as message: each list item starts at a new line
   """
   def __init__(self, error_type, info):
      Exception.__init__(self, error_type, info)
      self.__error_type = error_type
      self.__info = '\n'.join(info)
      self.__txt = '''

========================================================================
PySpeedIT-{} ERROR:


  {}

This `PySpeedIT` was tested with:
  HOST OS: {}
========================================================================

'''.format(self.__error_type, self.__info, TESTED_HOST_OS)
      print(self.__txt)


# ===========================================================================================================================
# public helpers
# ===========================================================================================================================
def build_cython_extension(py_or_pyx_file_path, cython_force_rebuild=True):
   """Build a cython extension from a `.py` or `.pyx` file

   - build will be done in a sub-folder named `_pyxbld` in the py_or_pyx_file_path

   :param py_or_pyx_file_path: (str) path to a `.py` or `.pyx` file
   :param cython_force_rebuild: (bool) If True the cython extension is rebuild even if it was already build
   :return: (tuple) cython_extension_module_path, cython_module_c_file_path, cython_build_dir_path
   """
   module_dir = path_dirname(py_or_pyx_file_path)
   module__cython_name = path_splitext(path_basename(py_or_pyx_file_path))[0]
   cython_module_c_file_path = path_join(module_dir, module__cython_name + '.c')
   cython_build_dir_path = path_join(module_dir, '_pyxbld')

   args = ['--quiet', 'build_ext', '--build-lib', module_dir]
   if cython_force_rebuild:
      args.append('--force')
   dist = Distribution({'script_name': None, 'script_args': args})
   dist.ext_modules = [Extension(name=module__cython_name, sources=[py_or_pyx_file_path])]
   dist.cmdclass = {'build_ext': cython_build_ext}
   build = dist.get_command_obj('build')
   build.build_base = cython_build_dir_path

   try:
      dist.parse_command_line()
   except DistutilsArgError as err:
      raise Err('utils.build_cython_extension', [
         'py_or_pyx_file_path: <{}>'.format(py_or_pyx_file_path),
         '  DistutilsArgError: <{}>'.format(err)
      ])

   try:
      obj_build_ext = dist.get_command_obj('build_ext')
      dist.run_commands()
      cython_extension_module_path = obj_build_ext.get_outputs()[0]
      if path_dirname(py_or_pyx_file_path) != module_dir:
         raise Err('utils.build_cython_extension', [
            'py_or_pyx_file_path: <{}>'.format(py_or_pyx_file_path),
            '  <module_dir> differs from final <cython_module_dir>',
            '   module_dir: <{}>'.format(module_dir),
            '   cython_module_dir: <{}>'.format(path_dirname(py_or_pyx_file_path))
         ])
   except Exception as err:
      raise Err('utils.build_cython_extension', [
         'py_or_pyx_file_path: <{}>'.format(py_or_pyx_file_path),
         '  Exception: <{}>'.format(err)
      ])

   return cython_extension_module_path, cython_module_c_file_path, cython_build_dir_path


def format_time(time_):
   """Returns a formatted time string in the Orders of magnitude (time)

   :param time_: (float) if if -1.0 return 'NOT-MEASURED''
   :return: (str) formatted time: Orders of magnitude (time)

      .. table:: Orders of magnitude (time)
         :column-alignment: left center left
         :column-dividers: none single single none

         =========== ====== ============================
         Name        Symbol Definition
         =========== ====== ============================
         second      ( s )  One second
         millisecond ( ms ) One thousandth of one second
         microsecond ( µs ) One millionth of one second
         nanosecond  ( ns ) One billionth of one second
         =========== ====== ============================
   """
   if time_ == -1.0:
      final_time_str = 'NOT-MEASURED'
   else:
      base = 1
      for unit in ['s', 'ms', 'us']:
         if time_ >= base:
            break
         base /= 1000
      else:
         unit = 'ns'
      final_time_str = '{:.2f} {}'.format(time_ / base, unit)
   return final_time_str


def get_html_template_css():
   """ Returns the css styles used by all: Benchmark-IT, Profile-IT, Line-Memory-Profile-IT, Disassemble-IT

   :return: (str) html css styles
   """
   return '''
         table, td, th {
            border : rgba(0, 0, 0, 0.3) solid 1px;
            border-collapse : collapse;
         }
         table {
            width : 100%;
         }
         td {
            padding : 5px;
         }
         .head_title {
            color : blue;
            background-color : whitesmoke;
            font-weight : bold;
            font-size-adjust : 0.70;
         }
         .head_module_path {
            color : black;
            background-color : #FCFCFC;
            font-weight : normal;
            text-align : right;
         }
         .head_module_info {
            color : black;
            background-color : #FCFCFC;
            font-weight : normal;
            text-align : left;
         }
         .head_parameter {
            color : black;
            background-color : #F5F5F5;
            font-weight : normal;
            text-align : left;
         }
         .head {
            color : black;
            background-color : #FFC6C6;
            font-weight : bold;
         }
         .row-odd {
            color : black;
            background-color : #FFFFFF;
         }
         .row-even {
            color : black;
            background-color : #FCF5EB;
         }
         '''
