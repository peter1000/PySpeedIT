"""
====================
PySpeedIT.profile_it
====================

Overview
========

Can be used *instead of python's profiler* and uses internally the `cProfiler`.

For usage see :mod:`PySpeedIT.speed_it`

**OUTPUT HTML**

.. image:: _static/profile_it_results.png
   :align: center


Functions
=========

.. autofunction:: profile_functions_in_module
"""
from operator import itemgetter
from os.path import join as path_join
from _lsprof import Profiler

from PySpeedIT.utils import (
   Err,
   format_time,
   get_html_template_css,
)


def get_html_table_template():
   """ Returns a html_table_template

   :return: (str) html_table_template
   """
   return '''
   <br>
   <br>
   <table>
      <thead>
      <tr>
         <th class="head_title" colspan="5"><b>Profile-IT function_name: `{head_title_func}`</b>
         </th>
      </tr>
      <tr>
         <th class="head_module_path" colspan="5">{head_module_path}
         </th>
      </tr>
      <tr>
         <th class="head_module_info" colspan="5">
            <strong>total_calls:</strong> {head_module_info_total_calls} &nbsp;
            <strong>primitive_calls:</strong> {head_module_info_primitive_calls} &nbsp;
            <strong>total_time:</strong>  {head_module_info_total_time} &nbsp;
         </th>
      </tr>
      <tr>
         <th class="head_parameter" rowspan="2">
            <strong>Parameters:</strong>
         </th>
         <th class="head_parameter" colspan="4">
            <strong>output_max_slashes_fileinfo:</strong> {head_parameter_output_max_slashes_fileinfo} &nbsp;
            <strong>use_func_name:</strong> {head_parameter_use_func_name}
         </th>
      </tr>
      <tr>
         <th class="head_parameter" colspan="4">
            <strong>output_in_sec:</strong> {head_parameter_output_in_sec} &nbsp;
            <strong>profileit__repeat:</strong> {head_parameter_profileit__repeat}
         </th>
      </tr>
      <tr>
         <th colspan="5">
            <br />
         </th>
      </tr>
      <tr class="head">
         <th>rank</th>
         <th>compare %</th>
         <th>func_time</th>
         <th>number_of_calls</th>
         <th>func_txt</th>
      </tr>
      </thead>

      <tfoot>
      <tr class="head">
         <th>rank</th>
         <th>compare %</th>
         <th>func_time</th>
         <th>number_of_calls</th>
         <th>func_txt</th>
      </tr>
      </tfoot>

      <tbody>
      {body_final_result_rows}
      </tbody>
   </table>
'''


def get_html_table_row_template():
   """ Returns a html_table_row_template

   :return: (str) html_table_row_template
   """
   return '''
         <tr class="{td_class}">
            <td>{td_rank}</td>
            <td>{td_compare_perc}</td>
            <td>{td_func_time}</td>
            <td>{td_number_of_calls}</td>
            <td>{td_func_txt}</td>
         </tr>
   '''


def create_stats(profiler_):
   """ Based on cProfile.py

   :param profiler_: (obj)  _lsprof.Profiler instance
   :return: (dict) profiler state dict: format: func, tuple: (pcalls, ncalls, tottime, cumtime, callers)

      .. table:: profiler state dict: tuple format
         :widths: 3 2 1
         :column-alignment: left center
         :column-wrapping: true true
         :column-dividers: none single

         =========== ====================
         tuple value Meaning
         =========== ====================
         pcalls      primitive call count
         ncalls      call count
         tottime     internal time
         cumtime     cumulative time
         =========== ====================
   """
   profiler_.disable()
   entries = profiler_.getstats()
   stats = {}
   callers_dicts = {}
   # call information
   for entry in entries:
      # label
      if isinstance(entry.code, str):
         func = ('~', 0, entry.code)  # built-in functions ('~' sorts at the end)
      else:
         func = (entry.code.co_filename, entry.code.co_firstlineno, entry.code.co_name)

      ncalls = entry.callcount  # ncalls column of pstats (before '/')
      pcalls = ncalls - entry.reccallcount  # ncalls column of pstats (after '/')
      tottime = entry.inlinetime  # tottime column of pstats
      cumtime = entry.totaltime  # cumtime column of pstats
      callers = {}
      callers_dicts[id(entry.code)] = callers
      stats[func] = pcalls, ncalls, tottime, cumtime, callers
   # sub_call information
   for entry in entries:
      if entry.calls:
         # label
         if isinstance(entry.code, str):
            func = ('~', 0, entry.code)  # built-in functions ('~' sorts at the end)
         else:
            func = (entry.code.co_filename, entry.code.co_firstlineno, entry.code.co_name)

         for sub_entry in entry.calls:
            try:
               callers = callers_dicts[id(sub_entry.code)]
            except KeyError:
               continue
            ncalls = sub_entry.callcount
            pcalls = ncalls - sub_entry.reccallcount
            tottime = sub_entry.inlinetime
            cumtime = sub_entry.totaltime
            if func in callers:
               prev = callers[func]
               ncalls += prev[0]
               pcalls += prev[1]
               tottime += prev[2]
               cumtime += prev[3]
            callers[func] = ncalls, pcalls, tottime, cumtime
   return stats


def _profile_it(func, func_positional_arguments, func_keyword_arguments, output_max_slashes_fileinfo, profileit__repeat):
   """ Returns a dictionary with the profile result: the function runs only once.

   .. note:: excludes a couple of not relative functions/methods

      - excludes: profiler.enable()
      - exclude: profiler.disable()
      - exclude: cProfile.Profile.runcall()

   :param func:
   :param func_positional_arguments: (list) positional arguments for the function
   :param func_keyword_arguments: (dict) any keyword arguments for the function
   :param output_max_slashes_fileinfo: (int) to adjust max path levels in the profile info
   :param profileit__repeat: (int) how often the function is repeated: the result will be the sum of all:
      similar to the code below

      .. code-block:: python

         for repeat in range(profileit__repeat):
            profiler.enable()
            profiler.runcall(func, *func_positional_arguments, **func_keyword_arguments)
            profiler.disable()

   :return: (tuple) format: (summary_dict, table): table = list_of_dictionaries (sorted profile result lines dict)
   :raise Err:
   """
   profiler = Profiler()

   for repeat in range(profileit__repeat):
      profiler.enable()
      func(*func_positional_arguments, **func_keyword_arguments)
      profiler.disable()

   total_calls = 0
   primitive_calls = 0
   total_time = 0
   table = []

   for func_tmp, (pcalls, ncalls, tottime, cumtime, callers) in create_stats(profiler).items():

      temp_dict = {
         'number_of_calls': '{:,}'.format(pcalls) if pcalls == ncalls else '{:,}/{:,}'.format(pcalls, ncalls),
         'func_time': tottime, 'func_cumulative_time': cumtime
      }

      if func_tmp[0] == '~':
         # exclude the profiler.enable()/disable() functions
         if '_lsprof.Profiler' in func_tmp[2]:
            continue
         else:
            temp_func_txt = func_tmp[2]
      else:
         # adjust path levels
         temp_path_file_ect = func_tmp[0]
         temp_slashes = temp_path_file_ect.count('/')
         if temp_slashes > output_max_slashes_fileinfo:
            temp_func_txt = '{}:{}({})'.format(
               temp_path_file_ect.split('/', temp_slashes - output_max_slashes_fileinfo)[-1],
               func_tmp[1], func_tmp[2]
            )
         else:
            temp_func_txt = '{}:{}({})'.format(temp_path_file_ect, func_tmp[1], func_tmp[2])

      if temp_func_txt[0] == '<' and temp_func_txt[-1] == '>':
         temp_dict['func_txt'] = temp_func_txt[1:-1]
      elif temp_func_txt[0] == '<':
         temp_dict['func_txt'] = temp_func_txt[1:]
      elif temp_func_txt[-1] == '>':
         temp_dict['func_txt'] = temp_func_txt[:-1]
      else:
         temp_dict['func_txt'] = temp_func_txt

      table.append(temp_dict)

      total_calls += ncalls
      primitive_calls += pcalls
      total_time += tottime
      if ("jprofile", 0, "profiler") in callers:
         raise Err('_profile_it', ['ERROR NOT SURE WHAT To DO HERE: SEE pstate.py: get_top_level_stats()', func])

   summary_dict = {
      'total_calls': total_calls,
      'primitive_calls': primitive_calls,
      'total_time': total_time
   }

   return summary_dict, table


def profile_functions_in_module(
      loaded_module,
      module_path,
      module_name,
      profiles_dir_path,
      module_tuple_of_func_tuples,
      output_max_slashes_fileinfo,
      use_func_name,
      output_in_sec,
      profileit__repeat):
   """ Writes the results for one loaded_module for all defined functions to a html files overwriting them if they existed.

   .. seealso::

      for the meaning of the parameters :py:func:`speed_it <PySpeedIT.speed_it.speed_it>`

   """
   final_html_table_profile = '''
   <!DOCTYPE html>
   <html>
   <head lang="en">
      <meta charset="UTF-8">
      <style type="text/css">
         {head_embedded_style_sheet}
      </style>
      <title>Profile-IT: {head_module_name}</title>
   </head>
   <body>

   '''.format(head_embedded_style_sheet=get_html_template_css(), head_module_name=module_name)

   for name_str, function_name_str, func_positional_arguments, func_keyword_arguments in module_tuple_of_func_tuples:
      try:
         func = getattr(loaded_module, function_name_str)
      except Exception as err:
         raise Err('_profile_functions_in_module', [
            'COULD NOT ACCESS FUNCTION ERROR: function_name_str: <{}>'.format(function_name_str),
            '  loaded_module: <{}>'.format(loaded_module),
            '    Exception: <{}>'.format(err)
         ])

      if use_func_name:
         name = getattr(func, "__name__", func)
      else:
         name = name_str
      summary_dict, table = _profile_it(func, func_positional_arguments, func_keyword_arguments, output_max_slashes_fileinfo,
         profileit__repeat)

      table = sorted(table, key=itemgetter('func_time'), reverse=True)
      compare_reference = summary_dict['total_time']
      if compare_reference == 0:
         # add ranking ect...
         for idx, dict_ in enumerate(table):
            dict_['compare'] = 'TOO-FAST-NOT-MEASURED'
            dict_['rank'] = '{:,}'.format(idx + 1)
            if output_in_sec:
               dict_['func_time'] = '{:.11f}'.format(dict_['func_time'])
            else:
               dict_['func_time'] = format_time(dict_['func_time'])
      else:
         # add ranking ect...
         for idx, dict_ in enumerate(table):
            dict_['compare'] = '{:,.3f}'.format((dict_['func_time'] * 100.0) / compare_reference)
            dict_['rank'] = '{:,}'.format(idx + 1)
            if output_in_sec:
               dict_['func_time'] = '{:.11f}'.format(dict_['func_time'])
            else:
               dict_['func_time'] = format_time(dict_['func_time'])

      final_result_rows = ''
      for row in table:
         rank = int(row['rank'])
         if (rank % 2) == 0:
            final_td_class = 'row-even'
         else:
            final_td_class = 'row-odd'

         final_result_rows += get_html_table_row_template().format(
            td_class=final_td_class,
            td_rank=row['rank'],
            td_compare_perc=row['compare'],
            td_func_time=row['func_time'],
            td_number_of_calls=row['number_of_calls'],
            td_func_txt=row['func_txt'],
         )

      if output_in_sec:
         total_time = '{:.11f}'.format(summary_dict['total_time'])
      else:
         total_time = format_time(summary_dict['total_time'])

      final_html_table_profile += get_html_table_template().format(
         head_title_func=name,
         head_module_path=module_path,
         head_module_info_total_calls=summary_dict['total_calls'],
         head_module_info_primitive_calls=summary_dict['primitive_calls'],
         head_module_info_total_time=total_time,

         head_parameter_output_max_slashes_fileinfo='{}'.format(output_max_slashes_fileinfo),
         head_parameter_use_func_name='{}'.format(use_func_name),

         head_parameter_output_in_sec='{}'.format(output_in_sec),
         head_parameter_profileit__repeat='{}'.format(profileit__repeat),

         body_final_result_rows=final_result_rows,
      )

   final_html_table_profile += '''
   </body>
   </html>
   '''
   with open(path_join(profiles_dir_path, 'profile_it__{}.html'.format(module_name)), 'w') as file_:
      file_.write(final_html_table_profile)
