""" Example implementation: <Speed-IT>
"""
from inspect import (
   getfile as inspect_getfile,
   currentframe as inspect_currentframe,
)
from os.path import (
   abspath as path_abspath,
   dirname as path_dirname,
   join as path_join,
)
from sys import path as sys_path


SCRIPT_PATH = path_dirname(path_abspath(inspect_getfile(inspect_currentframe())))
PROJECT_ROOT = path_dirname(SCRIPT_PATH)

ROOT_PACKAGE_NAME = 'PySpeedIT'
ROOT_PACKAGE_PATH = path_join(PROJECT_ROOT, ROOT_PACKAGE_NAME)

sys_path.insert(0, PROJECT_ROOT)

from PySpeedIT.speed_it import speed_it


data = dict(zip(range(1000), range(1000)))


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
def main():
   # defining the: modules_func_tuple mapping
   modules__func_tuples = (
      # TUPLE format:
      # [module_path_str, ((name_str, function_name_str, list_of_positional_arguments, dictionary_of_keyword_arguments))]

      [path_abspath('calculate_pi.py'), (
         ('calculate pi', 'approx_pi', [], {'n_': 100000}),
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
       [path_abspath('memory_example.py'), (
       ('memory_example1', 'memory_example1', [27], {'mul': 100}),
       ('memory_example2', 'memory_example2', [], {}),
       )],
   )

   speed_it(
      html_output_dir_path=path_abspath('result_output'),
      enable_benchmarkit=True,
      enable_profileit=True,
      enable_linememoryprofileit=True,
      enable_disassembleit=True,
      modules__func_tuples=modules__func_tuples,
      output_max_slashes_fileinfo=2,
      use_func_name=True,
      output_in_sec=False,
      profileit__repeat=1,
      benchmarkit__output_source=True,
      benchmarkit__with_gc=False,
      benchmarkit__check_too_fast=True,
      benchmarkit__rank_by='best',
      benchmarkit__run_sec=0.5,
      benchmarkit__repeat=3
   )


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
if __name__ == '__main__':
   main()
