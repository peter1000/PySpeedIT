"""
==================
PySpeedIT.speed_it
==================

Overview
========

This is the main module of *PySpeedIT*.
It is a combination of Benchmark-IT, Profile-IT, Line-Memory-Profile-IT, Disassemble-IT.


.. _speed-it-usage-example:

.. index:: PySpeedIT; usage, Usage; speed_it usage

Speed-It-Usage
==============

#. Define one or more separate modules with test functions.

   .. python-example::

      .. code-block:: python

         # file: usage_example.py

         from operator import itemgetter
         from random import shuffle


         def _outer_helper(y_):
            return y_[1]


         def example_pep265(data_):
            shuffle(data_)
            result = sorted(data_.items(), key=itemgetter(1))
            del result


         def example_formal_func_outer(data_):
            shuffle(data_)
            result = sorted(data_.items(), key=_outer_helper)
            del result


         # for Benchmark-IT subcode_blocks
         def example_multiple_subcode_blocks():
            # ::SPEEDIT:: data
            data = dict(zip(range(1000), range(1000)))
            # **SPEEDIT**
            shuffle(data)
            # ::SPEEDIT:: sorted
            result = sorted(data.items(), key=itemgetter(1))
            # **SPEEDIT**
            del result


         def memory_example():
            a = [1] * (10 ** 6)
            b = [2] * (2 * 10 ** 7)
            del b
            del a


#. Define an other module to run Speed-IT.

   .. python-example::

      .. code-block:: python

         # file: run_speed_it __usage_example.py

         # Import abspath
         from os.path import abspath as path_abspath

         # Import speed_it
         from PySpeedIT.speed_it import speed_it


         # define any needed extra variables to use as arguments
         data = dict(zip(range(1000), range(1000)))


         # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
         def main():
            # defining the: modules_func_tuple mapping
            modules__func_tuples = (
               # TUPLE format:
               # [module_path_str, (
               #   (name_str, function_name_str, list_of_positional_arguments, dictionary_of_keyword_arguments)
               # )]

               [path_abspath('usage_example.py'), (
                  ('sorting: pep265', 'example_pep265', [data], {}),
                  ('sorting: formal_func_outer', 'example_formal_func_outer', [data], {}),
                  ('multiple_subcode_blocks', 'example_multiple_subcode_blocks', [], {}),
                  ('memory_example', 'memory_example', [], {}),
               )],
               # any other module: a similar list
            )


   .. note::

      Do not import the module with the functions to speed-it the module is internally loaded  from file


For more *examples* see any files in the `PySpeedIT source` :samp:`{SOURCE}/Examples`

- especially the file: **run_speed_it.py**

.. index:: PySpeedIT; usage (common errors), Usage; usage (common errors)

Common Errors
-------------

Return statement in speed_it functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Function which are used for speed_it may not have a return statement because they may run in a loop

.. python-example::

   **WRONG** return statement

   .. code-block:: python

      # helper function is ok to have return statement
      def recip_square(i_):
         return 1.0 / (i_ ** 2)


      # function to be used by speed_it can not have a return statement
      def approx_pi(n_=100000):
         val = 0.
         for k_ in range(1, n_ + 1):
            val += recip_square(k_)
         return (6 * val) ** 0.5


Missing speed_it modules__func_tuples arguments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a function defines a default argument it still needs an argument passed on in the modules__func_tuples.

.. python-example::

   .. code-block:: python

      # function to be used by speed_it
      def approx_pi(n_=100000):
         val = 0.
         for k_ in range(1, n_ + 1):
            val += recip_square(k_)
         return (6 * val) ** 0.5

   **WRONG:** `modules__func_tuples` missing argument for : ``n_``

   .. code-block:: python

      modules__func_tuples = (
            # TUPLE format:
            # [module_path_str, ((name_str, function_name_str, list_of_positional_arguments, dictionary_of_keyword_arguments))]

            [path_abspath('calculate_pi.py'), (
               ('calculate pi', 'approx_pi', [], {}),
            )],
         )


   **OK:** `modules__func_tuples` with argument for : ``n_``

   .. code-block:: python

      modules__func_tuples = (
            # TUPLE format:
            # [module_path_str, ((name_str, function_name_str, list_of_positional_arguments, dictionary_of_keyword_arguments))]

            [path_abspath('calculate_pi.py'), (
               ('calculate pi', 'approx_pi', [], {'n_': 100000}),
            )],
         )


.. index:: PySpeedIT; screenshots of results output html

Screenshots of OUTPUT HTML
==========================

Benchmark-IT OUTPUT HTML
------------------------

.. image:: _static/benchmark_it_results.png
   :align: center

Profile-IT OUTPUT HTML
----------------------

.. image:: _static/profile_it_results.png
   :align: center

Line-Memory-Profile-IT OUTPUT HTML
----------------------------------

.. image:: _static/line_memory_profile_it_results.png
   :align: center

Disassemble-IT OUTPUT HTML
--------------------------

.. image:: _static/disassemble_it_results.png
   :align: center


Functions
=========

.. autofunction:: speed_it
"""
from importlib.machinery import SourceFileLoader
from os import (
   makedirs as os_makedirs,
)
from os.path import (
   basename as path_basename,
   splitext as path_splitext,
   join as path_join,
)

from PySpeedIT.benchmark_it import benchmark_functions_in_module
from PySpeedIT.disassemble_it import disassemble_functions_in_module
from PySpeedIT.line_memory_profile_it import line_memory_profile_functions_in_module
from PySpeedIT.profile_it import profile_functions_in_module
from PySpeedIT.utils import Err


def _helper_run_it(
      loaded_module,
      benchmarks_dir_path,
      profiles_dir_path,
      linememoryprofiles_dir_path,
      disassembles_dir_path,
      module_tuple_of_func_tuples,
      #
      enable_benchmarkit,
      enable_profileit,
      enable_linememoryprofileit,
      enable_disassembleit,
      # modules__func_tuples: not used
      output_max_slashes_fileinfo,
      use_func_name,
      output_in_sec,
      profileit__repeat,
      benchmarkit__output_source,
      benchmarkit__with_gc,
      benchmarkit__check_too_fast,
      benchmarkit__rank_by,
      benchmarkit__run_sec,
      benchmarkit__repeat):
   # ==========
   module_path = getattr(loaded_module, "__file__", loaded_module)
   module_name = getattr(loaded_module, "__name__", loaded_module)

   # adjust path levels
   temp_slashes = module_path.count('/')
   if temp_slashes > output_max_slashes_fileinfo:
      module_path = module_path.split('/', temp_slashes - output_max_slashes_fileinfo)[-1]

   if enable_benchmarkit:
      benchmark_functions_in_module(
         loaded_module,
         module_path,
         module_name,
         benchmarks_dir_path,
         module_tuple_of_func_tuples,
         output_max_slashes_fileinfo,
         use_func_name,
         output_in_sec,
         benchmarkit__output_source,
         benchmarkit__with_gc,
         benchmarkit__check_too_fast,
         benchmarkit__rank_by,
         benchmarkit__run_sec,
         benchmarkit__repeat
      )
   if enable_profileit:
      profile_functions_in_module(
         loaded_module,
         module_path,
         module_name,
         profiles_dir_path,
         module_tuple_of_func_tuples,
         output_max_slashes_fileinfo,
         use_func_name,
         output_in_sec,
         profileit__repeat
      )
   if enable_linememoryprofileit:
      line_memory_profile_functions_in_module(
         loaded_module,
         module_path,
         module_name,
         linememoryprofiles_dir_path,
         module_tuple_of_func_tuples,
         output_max_slashes_fileinfo,
         use_func_name,
      )
   if enable_disassembleit:
      disassemble_functions_in_module(
         loaded_module,
         module_path,
         module_name,
         disassembles_dir_path,
         module_tuple_of_func_tuples,
         output_max_slashes_fileinfo,
         use_func_name,
      )


def speed_it(
      html_output_dir_path=None,
      enable_benchmarkit=True,
      enable_profileit=True,
      enable_linememoryprofileit=True,
      enable_disassembleit=True,
      modules__func_tuples=None,
      output_max_slashes_fileinfo=2,
      use_func_name=True,
      output_in_sec=False,
      profileit__repeat=1,
      benchmarkit__output_source=False,
      benchmarkit__with_gc=False,
      benchmarkit__check_too_fast=True,
      benchmarkit__rank_by='best',
      benchmarkit__run_sec=1,
      benchmarkit__repeat=3):
   """ Writes the results per defined module to html files overwriting them if they existed.

   :param html_output_dir_path: Base directory to output the results
   :param enable_benchmarkit: enable/disable Benchmark-IT
   :param enable_profileit: enable/disable Profile-IT
   :param enable_linememoryprofileit: enable/disable Line-Memory-Profile-IT
   :param enable_disassembleit: enable/disable Disassemble-IT
   :param modules__func_tuples: (tuple)  TUPLE format:

      .. python-example::

         .. code-block:: python

            [module_path_str, (
               (name1_str, function1_name_str, list_of_positional_arguments, dictionary_of_keyword_arguments),
               (name2_str, function2_name_str, list_of_positional_arguments, dictionary_of_keyword_arguments),
            ]

         .. code-block:: python

            # defining the: modules_func_tuple mapping
            modules__func_tuples = (
               [path_abspath('calculate_pi.py'), (
                  ('calculate pi', 'approx_pi', [], {}),
               )],
               [path_abspath('dict_sorting.py'), (
                  ('sorting: pep265', 'example_pep265', [data], {}),
                  ('sorting: stupid', 'example_stupid', [data], {}),
                  ('sorting: list_expansion', 'example_list_expansion', [data], {}),
                  ('sorting: generator', 'example_generator', [data], {}),
                  ('sorting: lambda', 'example_lambda', [data], {}),
                  ('sorting: formal_func_inner', 'example_formal_func_inner', [data], {}),
                  ('sorting: formal_func_outer', 'example_formal_func_outer', [data], {}),
               )],
            )

   :param output_max_slashes_fileinfo: (int) to adjust max path levels in the module file info

      (as well the Profile-IT func_txt)

   :param use_func_name: (bool)

      - if True the function name will be used in the output `name`
      - if False the `func_dict key` will be used in the the output `name`

   :param output_in_sec: (bool)

      - if true the output is kept in seconds (float)
      - if false it is transformed to:

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

   :param profileit__repeat: (int) how often the function is repeated: the result will be the sum of all: similar to the code
      below

      .. code-block:: python

         for repeat in range(profileit__repeat):
            profiler.enable()
            profiler.runcall(func, *func_positional_arguments, **func_keyword_arguments)
            profiler.disable()

   :param benchmarkit__output_source: (bool) if True a text file is written with the actual Benchmark-IT code used
   :param benchmarkit__with_gc: (bool)

      - if True gc is kept on during timing
      - if False: turns off garbage collection during the timing

   :param benchmarkit__check_too_fast: (bool)

      - if True and a code block is executed faster than a `Reference-Time` an Exception is raised.

         - Reference-Time: the smallest difference of calling perf_counter() immediately after each other a couple of times

         .. seealso:: :py:func:`Reference-Time <PySpeedIT.benchmark_it._helper_get_perf_counter_reference_time>`

   :param benchmarkit__rank_by: (str) ``best`` or ``average``
   :param benchmarkit__run_sec: (float or -1)

      - the number of loops per run is scaled to approximately fit the benchmarkit__run_sec

      - if benchmarkit__run_sec is -1: then the generated function source code is only run once

   :param benchmarkit__repeat: (int) how often everything is repeated

      - This is a convenient variable that calls the whole Benchmark-IT setup repeatedly
   """
   if not html_output_dir_path:
      raise Err('speed_it', ['html_output_dir_path: <{}> needs to be set'.format(html_output_dir_path)])
   if not modules__func_tuples:
      raise Err('speed_it', ['modules__func_tuples: <{}> needs to be set'.format(modules__func_tuples)])

   if not (enable_benchmarkit or enable_profileit or enable_linememoryprofileit or enable_disassembleit):
      raise Err('speed_it', [
         'At least one of the modules must be enables:',
         ' BenchmarkIT: <{}> ProfileIT: <{}> LineMemoryProfileIT: <{}> DisassembleIT: <{}>'.format(
            enable_benchmarkit,
            enable_profileit,
            enable_linememoryprofileit,
            enable_disassembleit)
      ])

   # Prepare folders
   benchmarks_dir_path = path_join(html_output_dir_path, 'BenchmarkIT_Results')
   profiles_dir_path = path_join(html_output_dir_path, 'ProfileIT_Results')
   linememoryprofiles_dir_path = path_join(html_output_dir_path, 'LineMemoryIT_Results')
   disassembles_dir_path = path_join(html_output_dir_path, 'DisassembleIT_Results')

   if enable_benchmarkit:
      os_makedirs(benchmarks_dir_path, exist_ok=True)
      # do once some other checks
      if benchmarkit__rank_by != 'best' and benchmarkit__rank_by != 'average':
         raise Err('speed_it', [
            'enable_benchmarkit: <{}> >> <benchmarkit__rank_by> must be one of: <best, average> We got: <{}>'.format(
               enable_benchmarkit,
               benchmarkit__rank_by
            )
         ])
      if benchmarkit__repeat < 1:
         raise Err('speed_it', [
            'enable_benchmarkit: <{}> >> <benchmarkit__repeat> must be greater than <0> We got: <{}>'.format(
               enable_benchmarkit,
               benchmarkit__repeat
            )
         ])
   if enable_profileit:
      os_makedirs(profiles_dir_path, exist_ok=True)
   if enable_linememoryprofileit:
      os_makedirs(linememoryprofiles_dir_path, exist_ok=True)
   if enable_disassembleit:
      os_makedirs(disassembles_dir_path, exist_ok=True)

   for module_file_path, module_tuple_of_func_tuples, in modules__func_tuples:
      module_filename = path_basename(module_file_path)
      module_filename_no_extension = path_splitext(module_filename)[0]

      # NO: __init__
      if '__init__' in module_filename:
         raise Err('speed_it', [
            '<module_obj> may not contain the string <__init__>.',
            '  module_filename: <{}>'.format(module_filename),
            '    module_file_path entry: <{}>'.format(module_file_path)
         ])

      # ========== normal py
      try:
         py_loader = SourceFileLoader(module_filename_no_extension, module_file_path)
         py_mod = py_loader.load_module(module_filename_no_extension)
      except Exception as err:
         raise Err('speed_it', [
            'COULD NOT LOAD MODULE ERROR: module_file_path: <{}>'.format(module_file_path),
            '  Exception: <{}>'.format(err)
         ])
      # ==========
      _helper_run_it(
         py_mod,
         benchmarks_dir_path,
         profiles_dir_path,
         linememoryprofiles_dir_path,
         disassembles_dir_path,
         module_tuple_of_func_tuples,
         #
         enable_benchmarkit,
         enable_profileit,
         enable_linememoryprofileit,
         enable_disassembleit,
         # modules__func_tuples: not used
         output_max_slashes_fileinfo,
         use_func_name,
         output_in_sec,
         profileit__repeat,
         benchmarkit__output_source,
         benchmarkit__with_gc,
         benchmarkit__check_too_fast,
         benchmarkit__rank_by,
         benchmarkit__run_sec,
         benchmarkit__repeat
      )
