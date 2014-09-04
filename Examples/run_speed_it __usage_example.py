""" Example implementation: <Speed-IT> works only if PySpeedIT is in the path: example installed as: develop
"""

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
      benchmarkit__run_sec=0.1,
      benchmarkit__repeat=3
   )


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
if __name__ == '__main__':
   main()
