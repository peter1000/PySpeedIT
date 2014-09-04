# much of the code is based on: a reduced version of parts of: https://github.com/fabianp/memory_profiler
# memory_profiler: License: Simplified BSD

"""
================================
PySpeedIT.line_memory_profile_it
================================

Overview
========

A profiler that records the amount of memory for each line.

This code is based on parts of: `memory_profiler <https://github.com/fabianp/memory_profiler>`_.

For usage see :mod:`PySpeedIT.speed_it`

**OUTPUT HTML**

.. image:: _static/line_memory_profile_it_results.png
   :align: center


Functions
=========

.. autofunction:: line_memory_profile_functions_in_module
"""
from inspect import getblock
from linecache import getlines as linecache_getlines
from os import (
   getpid,
   path
)
from os.path import join as path_join
from sys import (
   settrace,
   gettrace
)

from psutil import Process

from PySpeedIT.utils import (
   Err,
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
         <th class="head_title" colspan="4"><b>Line-Memory-Profile-IT function_name: `{head_title_func}`</b>
         </th>
      </tr>
      <tr>
         <th class="head_module_path" colspan="4">{head_module_path}
         </th>
      </tr>
      <tr>
         <th class="head_module_info" colspan="4">
            <strong>max_mem:</strong> {head_module_info_max_mem} &nbsp;
         </th>
      </tr>
      <tr>
         <th class="head_parameter" rowspan="1">
            <strong>Parameters:</strong>
         </th>
         <th class="head_parameter" colspan="3">
            <strong>output_max_slashes_fileinfo:</strong> {head_parameter_output_max_slashes_fileinfo} &nbsp;
            <strong>use_func_name:</strong> {head_parameter_use_func_name}
         </th>
      </tr>
      <tr>
         <th colspan="4">
            <br />
         </th>
      </tr>
      <tr class="head">
         <th>line num</th>
         <th>memory_usage</th>
         <th>incr. memory_usage</th>
         <th>line</th>
      </tr>
      </thead>

      <tfoot>
      <tr class="head">
         <th>line num</th>
         <th>memory_usage</th>
         <th>incr. memory_usage</th>
         <th>line</th>
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
            <td>{td_line_num}</td>
            <td>{td_memory_usage}</td>
            <td>{td_increment_memory_usage}</td>
            <td>{td_line}</td>
         </tr>
   '''


class _LineMemoryProfiler(object):
   """ A profiler that records the amount of memory for each line

   This code is a reduced version of parts of: https://github.com/fabianp/memory_profiler
   License: Simplified BSD
   """

   def __init__(self):
      """ Constructor.
      """
      self.code_map = {}
      self.enable_count = 0
      self.max_mem = None
      self.prevline = None
      self._original_trace_function = gettrace()


   def __call__(self, func):
      """ Called when the instance is `called` as a function

      :param func: (function)
      :return: (function) wrap_func
      """
      code = None
      try:
         code = func.__code__
      except AttributeError:
         Err('_LineMemoryProfiler', ['Could not extract a code object for the object: <{!r}>'.format(func)])
      if code not in self.code_map:
         self.code_map[code] = {}
      func_ = self.wrap_function(func)
      func_.__module__ = func.__module__
      func_.__name__ = func.__name__
      func_.__doc__ = func.__doc__
      func_.__dict__.update(getattr(func, '__dict__', {}))
      return func_


   def wrap_function(self, func):
      """ Wrap a function to *line memory profile it*.

      :param func: (function)
      :return: (function) wrap_func
      """

      def wrap_func(*args, **kwargs):
         """ inner wrap_func """
         if self.enable_count == 0:
            self._original_trace_function = gettrace()
            settrace(self.trace_memory_usage)
         self.enable_count += 1
         try:
            result = func(*args, **kwargs)
         finally:
            if self.enable_count > 0:
               self.enable_count -= 1
               if self.enable_count == 0:
                  settrace(self._original_trace_function)
         return result

      return wrap_func


   def trace_memory_usage(self, frame, event, arg):
      """ Callback for sys.settrace

      :param frame: frame is the current stack frame
      :param event: (str) event is a string: 'call', 'line', 'return', 'exception', 'c_call', 'c_return', or 'c_exception'
      :param arg: arg depends on the event type.
      :return: (function) wrap_func
      """
      if event in ('call', 'line', 'return') and frame.f_code in self.code_map:
         if event != 'call':
            # "call" event just saves the lineno but not the memory
            process = Process(getpid())
            mem = process.memory_info()[0] / float(2 ** 20)
            # if there is already a measurement for that line get the max
            old_mem = self.code_map[frame.f_code].get(self.prevline, 0)
            self.code_map[frame.f_code][self.prevline] = max(mem, old_mem)
         self.prevline = frame.f_lineno

      if self._original_trace_function is not None:
         self._original_trace_function(frame, event, arg)

      return self.trace_memory_usage


def _memory_profile_it(mem_profiler):
   """ Returns a dictionary with the memory profile result

   :param mem_profiler: (class) instance of `_LineMemoryProfiler`
   :return: (tuple) format: (max_mem, table): table = list_of_dictionaries
   """
   table = []
   max_mem = 0
   for code in mem_profiler.code_map:
      lines = mem_profiler.code_map[code]

      if not lines:
         # .. measurements are empty ..
         continue
      filename = code.co_filename
      if filename.endswith(('.pyc', '.pyo')):
         filename = filename[:-1]
      if not path.exists(filename):
         print('\n_memory_profile_it() ERROR: Could not find file: {}'.format(filename))
         continue
      all_lines = linecache_getlines(filename)
      sub_lines = getblock(all_lines[code.co_firstlineno - 1:])
      mem_old = lines[min(lines.keys())]
      for line in range(code.co_firstlineno, code.co_firstlineno + len(sub_lines)):
         mem = 0.0
         mem_increment = 0.0
         if line in lines:
            mem = lines[line]
            if mem > max_mem:
               max_mem = mem
            mem_increment = mem - mem_old
            mem_old = mem
         dict_ = {
            'line_num': '{}'.format(line),

            'memory_usage': '{:.3f} MiB'.format(mem),
            'increment_memory_usage': '{:.3f} MiB'.format(mem_increment),
            'line': all_lines[line - 1].strip()
         }
         table.append(dict_)

   max_mem = '{:.3f} MiB'.format(max_mem)
   return max_mem, table


def line_memory_profile_functions_in_module(
      loaded_module,
      module_path,
      module_name,
      linememoryprofiles_dir_path,
      module_tuple_of_func_tuples,
      output_max_slashes_fileinfo,
      use_func_name):
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
      <title>Line-Memory-Profile-IT: {head_module_name}</title>
   </head>
   <body>

   '''.format(head_embedded_style_sheet=get_html_template_css(), head_module_name=module_name)

   for name_str, function_name_str, func_positional_arguments, func_keyword_arguments in module_tuple_of_func_tuples:
      try:
         func = getattr(loaded_module, function_name_str)
      except Exception as err:
         raise Err('_line_memory_profile_functions_in_module', [
            'COULD NOT ACCESS FUNCTION ERROR: function_name_str: <{}>'.format(function_name_str),
            '  loaded_module: <{}>'.format(loaded_module),
            '    Exception: <{}>'.format(err)
         ])
      if use_func_name:
         name = getattr(func, "__name__", func)
      else:
         name = name_str

      profiler = _LineMemoryProfiler()
      profiler(func)(*func_positional_arguments, **func_keyword_arguments)
      max_mem, table = _memory_profile_it(profiler)

      final_result_rows = ''
      for idx, row in enumerate(table):
         if (idx % 2) == 0:
            final_td_class = 'row-even'
         else:
            final_td_class = 'row-odd'

         final_result_rows += get_html_table_row_template().format(
            td_class=final_td_class,
            td_line_num=row['line_num'],
            td_memory_usage=row['memory_usage'],
            td_increment_memory_usage=row['increment_memory_usage'],
            td_line=row['line'],
         )

      final_html_table_profile += get_html_table_template().format(
         head_title_func=name,
         head_module_path=module_path,
         head_module_info_max_mem=max_mem,

         head_parameter_output_max_slashes_fileinfo='{}'.format(output_max_slashes_fileinfo),
         head_parameter_use_func_name='{}'.format(use_func_name),

         body_final_result_rows=final_result_rows,
      )

   final_html_table_profile += '''
   </body>
   </html>
   '''
   with open(path_join(linememoryprofiles_dir_path, 'linememoryprofiles_it__{}.html'.format(module_name)), 'w') as file_:
      file_.write(final_html_table_profile)
