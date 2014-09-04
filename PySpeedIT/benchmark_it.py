"""
======================
PySpeedIT.benchmark_it
======================

Overview
========
Can be used *instead of python's timeit*.

*Benchmark-IT* supports also timing of only selected code parts within a function using *Comment lines* with a START/END TAG.

.. code-block:: python

   START-TAG: # ::SPEEDIT::
   END-TAG:   # **SPEEDIT**

.. important::

   Only functions within one module can be compared to each other for ranking

      - multiple modules can be run at once just ranking is restricted to functions within one module


For usage see :mod:`PySpeedIT.speed_it`

**OUTPUT HTML**

.. image:: _static/benchmark_it_results.png
   :align: center


Functions
=========

.. autofunction:: _helper_get_perf_counter_reference_time

.. autofunction:: benchmark_functions_in_module
"""
# noinspection PyUnresolvedReferences
from gc import (
   disable as gc_disable,
   enable as gc_enable,
   isenabled as gc_isenabled,
)
from inspect import (
   getsourcelines as inspect_getsourcelines,
   signature as inspect_signature,
)
from operator import itemgetter
from os.path import join as path_join
from time import perf_counter

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
         <th class="head_title" colspan="10"><b>Benchmark-IT module_name: `{head_title_func}`</b>
         </th>
      </tr>
      <tr>
         <th class="head_module_path" colspan="10">
            <strong>module_path:</strong> {head_module_path}
         </th>
      </tr>
      <tr>
         <th class="head_module_info" colspan="10">
            <strong>Number of functions:</strong> {head_module_num_functions}
         </th>
      </tr>
      <tr>
         <th class="head_parameter" rowspan="2">
            <strong>Parameters:</strong>
         </th>
         <th class="head_parameter" colspan="9">
            <strong>output_max_slashes_fileinfo:</strong> {head_parameter_output_max_slashes_fileinfo} &nbsp;
            <strong>use_func_name:</strong> {head_parameter_use_func_name}
         </th>
      </tr>
      <tr>
         <th class="head_parameter" colspan="9">
            <strong>output_in_sec:</strong> {head_parameter_output_in_sec} &nbsp;
            <strong>benchmarkit__output_source:</strong> {head_parameter_benchmarkit__output_source} &nbsp;
            <strong>benchmarkit__with_gc:</strong> {head_parameter_benchmarkit__with_gc} &nbsp;
            <strong>benchmarkit__check_too_fast:</strong> {head_parameter_benchmarkit__check_too_fast} &nbsp;
            <strong>benchmarkit__rank_by:</strong> {head_parameter_benchmarkit__rank_by} &nbsp;
            <strong>benchmarkit__run_sec:</strong> {head_parameter_benchmarkit__run_sec} &nbsp;
            <strong>benchmarkit__repeat:</strong> {head_parameter_benchmarkit__repeat} &nbsp;
         </th>
      </tr>
      <tr>
         <th colspan="10">
            <br />
         </th>
      </tr>
      <tr class="head">
         <th>name</th>
         <th>{head_thead_benchmarkit__rank_by}</th>
         <th>compare %</th>
         <th>num. loops</th>
         <th>avg_loop</th>
         <th>best_loop</th>
         <th>second_best_loop</th>
         <th>worst_loop</th>
         <th>second_worst_loop</th>
         <th>all_loops time</th>
      </tr>
      </thead>

      <tfoot>
      <tr class="head">
         <th>name</th>
         <th>{head_tfoot_benchmarkit__rank_by}</th>
         <th>compare %</th>
         <th>num. loops</th>
         <th>avg_loop</th>
         <th>best_loop</th>
         <th>second_best_loop</th>
         <th>worst_loop</th>
         <th>second_worst_loop</th>
         <th>all_loops time</th>
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
            <td>{td_name}</td>
            <td>{td_rank}</td>
            <td>{td_compare}</td>
            <td>{td_num_loops}</td>
            <td>{td_avg_loop}</td>
            <td>{td_best_loop}</td>
            <td>{td_second_best_loop}</td>
            <td>{td_worst_loop}</td>
            <td>{td_second_worst_loop}</td>
            <td>{td_all_loops_time}</td>
         </tr>
   '''


def _helper_get_perf_counter_reference_time():
   """ Returns 2 times the smallest difference of calling perf_counter() immediately after each other a couple of times.

   :return: (float) 2 times the smallest difference of calling perf_counter() immediately after each other a couple of times.
   """
   _result_time = 99999999999.0
   for y_ in range(50):
      for x_ in range(3000):
         temp_start = perf_counter()
         temp_time = perf_counter() - temp_start
         if temp_time < _result_time:
            _result_time = temp_time
   return _result_time * 2


class _TimeIT(object):
   """ Class for timing execution speed of function code.

   Partially based on code from python timeit.py

   This does not execute the original function but generates a new function which executes only the code body
   of 'func': `func code block`.

   This avoids calling into the function itself

   :param func: (function)

      .. warning:: the `func` function may not have any return statements: but any inner function can have one

      OK

      .. code-block:: python

         def example_formal_func_inner(data_):
            shuffle(data_)
            def fn_inner(x):
               return x[1]
            result = sorted(data_.items(), key=fn_inner)
            del result

      NOT OK

      .. code-block:: python

         def example_pep265(data_):
            shuffle(data_)
            result = sorted(data_.items(), key=itemgetter(1))
            return result

   :param orig_func_name: (str)
   :param module_globals: globals of the module where the function is defined in (e.g.: loaded_module.__dict__)
   :param args_list: (list) positional arguments for the function
   :param kwargs_dict: (dict) any keyword arguments for the function
   :param check_too_fast: (bool) if True and a code block is timed faster than a `Reference-Time` an Exception is raised.

      - Reference-Time: the smallest difference of calling perf_counter() immediately after each other a couple of times

      .. seealso:: _helper_get_perf_counter_reference_time()

   :param run_sec: (float or -1) seconds the `func code block` will be executed (looped over)

         - if run_sec is -1: then the generated function source code is only run once

   :param name: (str) the name used for the output `name` part
   :param perf_counter_reference_time: (float) passed on see: _helper_get_perf_counter_reference_time()
   """
   def __init__(self, func, orig_func_name, module_globals, args_list, kwargs_dict, check_too_fast, run_sec, name,
                perf_counter_reference_time):
      """ Constructor.
      """
      self.func = func
      self.orig_func_name = orig_func_name
      self.args_list = args_list.copy()
      self.kwargs_dict = kwargs_dict.copy()
      self.check_too_fast = check_too_fast
      self.run_sec = run_sec
      self.name = name
      self.perf_counter_reference_time = perf_counter_reference_time
      if callable(self.func):
         _ns = {}
         self.src = self.__get_final_inner_function()
         if self.run_sec != -1 and self.run_sec < 0.1:
            raise Err('_TimeIT.__init__', [
               '''run_sec: <{:.1f}> must be at least <0.1 second> or <-1 to run it once> or <None prints `func code block`>
               '''.format(self.run_sec)
            ])

         _code = compile(self.src, 'benchmarkit-src', "exec")
         # exec(_code, globals(), _ns)
         exec(_code, module_globals, _ns)

         self.inner = _ns["inner"]
      else:
         raise ValueError('<func>: is not a `callable` type: <{}>'.format(self.func))

   def get_source(self):
      """ Returns the actual used source code """
      return self.src

   def benchmark_it(self, with_gc):
      """ Returns timing result for the `func code block`

      :param with_gc:

       .. note::

         By default, timeit() temporarily turns off garbage collection during the timing.
         The advantage of this approach is that it makes independent timings more comparable.
         This disadvantage is that GC may be an important component of the performance of the function being measured.
         If so, GC can be re-enabled as the with_gc=True

      :return: dict benchmark result dict keys: loops, all_loops_time_sec, avg_loop_sec, best_loop_sec, worst_loop_sec

         - loops: how many times the  `func code block` was executed (looped over)
         - all_loops_time_sec: the total time in seconds for all loops:
            only loop times are counted not other times: depending on the `func code block` this can be about 25% of the
            total runtime
         - avg_loop_sec: average loop time in seconds: this should be mostly used as measure time:
            if there where only a very low number of loops - one might want to increase the `run_sec` and rerun it
         - two_best_loop_sec: time in seconds for the two fastest of all loops
         - two_worst_loop_sec: time in seconds for the two slowest of all loops
      """
      if with_gc:
         gc_old = gc_isenabled()
         gc_enable()
         try:
            benchmark_result = self.inner()
            benchmark_result['name'] = self.name
         finally:
            if not gc_old:
               gc_disable()
      else:
         gc_old = gc_isenabled()
         gc_disable()
         try:
            benchmark_result = self.inner()
            benchmark_result['name'] = self.name
         finally:
            if gc_old:
               gc_enable()
      return benchmark_result

   # noinspection PyPep8
   def __get_final_inner_function(self):
      """ Returns a string of an generated inner function with the code body from: func

      Tries to generate a new function with the 'code-body' from the `self.func`
      as well as the `self.args_list` and `self.kwargs_dict`

      :return: (str) generated inner function)
      :raise Err: example if an indentation is encountered which is not a multiple of the first found indentation
      """
      has_block_speedit = False
      _start_block_stripped_line = ''
      start_tag_block_speedit = 0
      end_tag_block_speedit = 0

      func_line, l_num = inspect_getsourcelines(self.func)
      sig = inspect_signature(self.func)
      indent_ = None
      func_def_indent = len(func_line[0]) - len(func_line[0].lstrip())
      func_body = func_line[1:]
      search_docstring = False

      # PREPARE: remove docstring and get final indentation
      first_none_docstring_idx = 0
      for idx, line_orig in enumerate(func_body):
         rstripped_line = line_orig.rstrip()
         if rstripped_line:
            stripped_codeline = rstripped_line.lstrip()
            if stripped_codeline[0] == '#':  # remove comment lines
               if not ('::SPEEDIT::' in stripped_codeline or '**SPEEDIT**' in stripped_codeline):
                  continue
            if search_docstring:
               if stripped_codeline[0:3] == '"""' or stripped_codeline[0:3] == "'''":
                  search_docstring = False
               continue
            else:
               codebody_indent = len(rstripped_line) - len(stripped_codeline)
               indent_ = codebody_indent - func_def_indent
               # Check if we have a docstring
               if stripped_codeline[0:3] == '"""' or stripped_codeline[0:3] == "'''":
                  search_docstring = True
                  continue
            first_none_docstring_idx = idx
            break

      # do the func code body
      adjusted_func_code_line = []
      for line_orig in func_body[first_none_docstring_idx:]:
         # remove empty
         if line_orig:
            # get indentation check it is a multiple of indent_
            rstrip_line = line_orig.rstrip()
            if rstrip_line:
               stripped_line = rstrip_line.lstrip()
               if stripped_line[0] == '#':  # remove comment lines: keep any with  ::SPEEDIT::
                  if '::SPEEDIT::' in stripped_line or '**SPEEDIT**' in stripped_line:
                     has_block_speedit = True
                  else:
                     continue
               line_indentation = len(rstrip_line) - len(stripped_line)
               if line_indentation % indent_ != 0:
                  raise Err('_TimeIT.get_final_inner_function', [
                     '<{}>: ERROR: indentation must be a multiple of the second function line: <{}>'.format(
                        self.orig_func_name,
                        indent_
                     ),
                     '  seems we encountered a wrong indented line: line_indentation: <{}>'.format(line_indentation),
                     '    {}'.format(line_orig)
                  ])
               line_indentation_level = int((line_indentation - func_def_indent) / indent_) + 1  # need one extra level

               if has_block_speedit:
                  if '::SPEEDIT::' in stripped_line:
                     if start_tag_block_speedit != end_tag_block_speedit:
                        # expected END Tag
                        raise Err('_TimeIT.get_final_inner_function', [
                           '<{}>: FUNCTION INNER TAG ERROR: has_block_speedit: <{}>'.format(
                              self.orig_func_name,
                              has_block_speedit
                           ),
                           '  Expected an END-TAG <**SPEEDIT**>: '
                           ' {}'.format(line_orig)
                        ])
                     adjusted_func_code_line.append(
                        ('   ' * line_indentation_level) + '_speedit_prefix__stmt_inner_start = _speedit_prefix__perf_counter()  # ::SPEEDIT::START internally added'
                     )
                     start_tag_block_speedit += 1
                     _start_block_stripped_line = stripped_line
                  elif '**SPEEDIT**' in stripped_line:
                     if end_tag_block_speedit != start_tag_block_speedit - 1:
                        # expected START TAG
                        raise Err('_TimeIT.get_final_inner_function', [
                           '<{}>: FUNCTION INNER TAG ERROR: has_block_speedit: <{}>'.format(
                              self.orig_func_name,
                              has_block_speedit),
                           '  Expected an START-TAG <::SPEEDIT::>:',
                           ' {}'.format(line_orig)
                        ])
                     # Do this inner result
                     adjusted_func_code_line.append((
                                                    '   ' * line_indentation_level) + '_speedit_prefix__result_time += _speedit_prefix__perf_counter() - _speedit_prefix__stmt_inner_start  # **SPEEDIT**END internally added')
                     if self.check_too_fast:
                        adjusted_func_code_line.append(
                           ('   ' * line_indentation_level) + 'if _speedit_prefix__result_time < _speedit_prefix__check_reference_time: raise Exception("in function: <{}>'.format(
                           self.orig_func_name) + ' code block: too fast to measure:\\n   code part: _speedit_prefix__result_time: <{:.11f}>  2 times _smallest_perf_counter_time: <{:.11f}>\\n  ' + '  _start_block_stripped_line: <{}>'.format(
                           _start_block_stripped_line) + '".format(_speedit_prefix__result_time, _speedit_prefix__check_reference_time))  # SPEEDIT: internally added')
                     end_tag_block_speedit += 1
                  else:
                     adjusted_func_code_line.append(('   ' * line_indentation_level) + stripped_line)
               else:
                  adjusted_func_code_line.append(('   ' * line_indentation_level) + stripped_line)

      # CHECK: LAST END TAG
      # e.g. if a function body ends with an END-TAG this is not returned by: inspect.getsourcelines(self.func)
      if has_block_speedit:
         if start_tag_block_speedit != end_tag_block_speedit:
            # Do the last inner result: ADDING an END-TAG
            adjusted_func_code_line.append(
               '      _speedit_prefix__result_time += _speedit_prefix__perf_counter() - _speedit_prefix__stmt_inner_start  # **SPEEDIT**END internally added')
            if self.check_too_fast:
               adjusted_func_code_line.append(
                  '      if _speedit_prefix__result_time < _speedit_prefix__check_reference_time: raise Exception("in function: <{}>'.format(
                     self.orig_func_name) + ' code block: too fast to measure:\\n   code part: _speedit_prefix__result_time: <{:.11f}>  2 times _smallest_perf_counter_time: <{:.11f}>\\n  ' + '  _start_block_stripped_line: <{}>'.format(
                     _start_block_stripped_line) + '".format(_speedit_prefix__result_time, _speedit_prefix__check_reference_time))  # SPEEDIT: internally added')

      # add the normal perf_counter time lines
      else:
         adjusted_func_code_line.insert(
            0,
            '      _speedit_prefix__stmt_inner_start = _speedit_prefix__perf_counter()  # ::SPEEDIT::START internally added'
         )
         adjusted_func_code_line.append(
            '      _speedit_prefix__result_time += _speedit_prefix__perf_counter() - _speedit_prefix__stmt_inner_start  # **SPEEDIT**END internally added')

         if self.check_too_fast:
            adjusted_func_code_line.append(
               '      if _speedit_prefix__result_time < _speedit_prefix__check_reference_time: raise Exception("in function: <{}>'.format(
                  self.orig_func_name) + ' code block: too fast to measure:\\n   code part: _speedit_prefix__result_time: <{:.11f}>  2 times _smallest_perf_counter_time: <{:.11f}>".format(_speedit_prefix__result_time, _speedit_prefix__check_reference_time))  # SPEEDIT: internally added')

      # Do the arguments
      final_param_line = []
      for param, value in sig.parameters.items():
         if value.kind == value.POSITIONAL_OR_KEYWORD:
            # check if we have a keyword
            if param in self.kwargs_dict:
               value_to_set = self.kwargs_dict.pop(param)
            else:  # use any positional
               if not self.args_list:
                  raise Err('_TimeIT.__get_final_inner_function', [
                     'orig_func_name: <{}>'.format(self.orig_func_name),
                     '  POSITIONAL_OR_KEYWORD ERROR: seems no such keyword nor enough positional arguments are supplied',
                     '   param: <{}>'.format(param),
                     '    list_of_positional_arguments: <{}>'.format(self.args_list),
                     '     dictionary_of_keyword_arguments: <{}>'.format(self.kwargs_dict),
                  ])
               value_to_set = self.args_list.pop(0)
            if isinstance(value_to_set, str):
               parameter_line = '{} = "{}"'.format(param, value_to_set)
            else:
               parameter_line = '{} = {}'.format(param, value_to_set)
            final_param_line.append(('   ' * 2) + parameter_line)
         elif value.kind == value.POSITIONAL_ONLY:
            value_to_set = self.args_list.pop(0)
            if isinstance(value_to_set, str):
               parameter_line = '{} = "{}"'.format(param, value_to_set)
            else:
               parameter_line = '{} = {}'.format(param, value_to_set)
            final_param_line.append(('   ' * 2) + parameter_line)
            # TODO: From docs: 3.4 Python has no explicit syntax for defining positional-only parameters, but many built-in and extension module functions (especially those that accept only one or two parameters) accept them.
            raise Err('_TimeIT.get_final_inner_function()', [
               'orig_func_name: <{}>'.format(self.orig_func_name),
               '  POSITIONAL_ONLY !! not sure what to do .. check in future if needed:',
               '   param: <{}> value.kind: <{}>'.format(param, value.kind)
            ])
         elif value.kind == value.VAR_POSITIONAL:  # do the remaining POSITIONAL arguments
            parameter_line = '{} = {}'.format(param, self.args_list)
            final_param_line.append(('   ' * 2) + parameter_line)
         elif value.kind == value.KEYWORD_ONLY:
            if param in self.kwargs_dict:
               value_to_set = self.kwargs_dict.pop(param)
            else:  # use the default
               value_to_set = value.default
            if isinstance(value_to_set, str):
               parameter_line = '{} = "{}"'.format(param, value_to_set)
            else:
               parameter_line = '{} = {}'.format(param, value_to_set)
            final_param_line.append(('   ' * 2) + parameter_line)
         elif value.kind == value.VAR_KEYWORD:  # do the remaining KEYWORD arguments
            parameter_line = '{} = {}'.format(param, self.kwargs_dict)
            final_param_line.append(('   ' * 2) + parameter_line)
         else:
            continue

      final_inner_function_lines = [
         'def inner():  # orig function name: {}'.format(self.orig_func_name),
         '   from time import perf_counter as _speedit_prefix__perf_counter',
         '',
         '   _speedit_prefix__run_sec = {}'.format(self.run_sec),
         '',
         '   # The smallest difference of calling _speedit_prefix__perf_counter() ',
         '   #   immediately after each other a couple of times',
         '   _speedit_prefix__check_reference_time = {}'.format(self.perf_counter_reference_time),
         '   _speedit_prefix__loops = 0',
         '   _speedit_prefix__all_loops_time_sec = 0.0',
         '   _speedit_prefix__avg_loop_sec = 0.0',
         '   _speedit_prefix__best_loop_sec = 99999999999.0',
         '   _speedit_prefix__second_best_loop_sec = 99999999999.0',
         '   _speedit_prefix__worst_loop_sec = 0.0',
         '   _speedit_prefix__second_worst_loop_sec = 0.0',
         '   if _speedit_prefix__run_sec == -1:',
         '      # only run it once',
         '      _speedit_prefix__run_once = True',
         '   else:',
         '      _speedit_prefix__run_once = False',
         '   _speedit_prefix__main_start_time = _speedit_prefix__perf_counter()',
         '   while True:',
         '      _speedit_prefix__loops += 1',
         '      _speedit_prefix__result_time = 0',
         '',
         '      # ==================== START CODE BLOCK ==================== #',
         '',
      ]

      final_inner_function_lines.extend(final_param_line)
      final_inner_function_lines.extend(adjusted_func_code_line)

      inner_function_lines_rest = [
         '',
         '      # ==================== END CODE BLOCK ==================== #',
         '',
         '      _speedit_prefix__all_loops_time_sec += _speedit_prefix__result_time',
         '      if _speedit_prefix__result_time <= _speedit_prefix__best_loop_sec:',
         '         _speedit_prefix__second_best_loop_sec = _speedit_prefix__best_loop_sec',
         '         _speedit_prefix__best_loop_sec = _speedit_prefix__result_time',
         '      if _speedit_prefix__result_time >= _speedit_prefix__worst_loop_sec:',
         '         _speedit_prefix__second_worst_loop_sec = _speedit_prefix__worst_loop_sec',
         '         _speedit_prefix__worst_loop_sec = _speedit_prefix__result_time',
         '      if _speedit_prefix__run_once:',
         '         break',
         '      # check if we have to get out',
         '      if _speedit_prefix__perf_counter() - _speedit_prefix__main_start_time >= _speedit_prefix__run_sec:',
         '         break',
         '   _speedit_prefix__avg_loop_sec = _speedit_prefix__all_loops_time_sec / _speedit_prefix__loops',
         '   if _speedit_prefix__second_best_loop_sec == 99999999999.0:',
         '      _speedit_prefix__second_best_loop_sec = -1.0',
         '   if _speedit_prefix__second_worst_loop_sec == 0.0:',
         '      _speedit_prefix__second_worst_loop_sec = -1.0',
         '   return {',
         '      "loops": _speedit_prefix__loops,',
         '      "all_loops_time_sec": _speedit_prefix__all_loops_time_sec,',
         '      "avg_loop_sec": _speedit_prefix__avg_loop_sec,',
         '      "best_loop_sec": _speedit_prefix__best_loop_sec,',
         '      "second_best_loop_sec": _speedit_prefix__second_best_loop_sec,',
         '      "worst_loop_sec": _speedit_prefix__worst_loop_sec,',
         '      "second_worst_loop_sec": _speedit_prefix__second_worst_loop_sec',
         '   }',
         ''
      ]
      final_inner_function_lines.extend(inner_function_lines_rest)

      return '\n'.join(final_inner_function_lines)


def benchmark_functions_in_module(
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
      benchmarkit__repeat):
   """ Writes the results for one loaded_module for all defined functions to a html files overwriting them if they existed.

   .. seealso::

      for the meaning of the parameters :py:func:`speed_it <PySpeedIT.speed_it.speed_it>`

   """
   # get once the perf_counter_reference_time
   perf_counter_reference_time = _helper_get_perf_counter_reference_time()

   # === DO THE SOURCE CODE
   if benchmarkit__output_source:
      all_final_lines = []
      # Run all only once and get the code
      for name_str, function_name_str, func_positional_arguments, func_keyword_arguments in module_tuple_of_func_tuples:
         try:
            func = getattr(loaded_module, function_name_str)
         except Exception as err:
            raise Err('_profile_functions_in_module', [
               'COULD NOT ACCESS FUNCTION ERROR: function_name_str: <{}>'.format(function_name_str),
               '  loaded_module: <{}>'.format(loaded_module),
               '    Exception: <{}>'.format(err)
            ])

         orig_func_name = getattr(func, "__name__", func)
         if use_func_name:
            name = orig_func_name
         else:
            name = name_str

         source_result = _TimeIT(
            func,
            orig_func_name,
            loaded_module.__dict__,
            func_positional_arguments,
            func_keyword_arguments,
            benchmarkit__check_too_fast,
            benchmarkit__run_sec,
            name,
            perf_counter_reference_time
         ).get_source()

         all_final_lines.extend([
            '===================== function name: <{}>'.format(name_str),
            '',
            source_result,
            '',
            '',
         ])

      with open(path_join(benchmarks_dir_path, 'benchmark_it__{}__code.txt'.format(module_name)), 'w') as file_:
         file_.write('\n'.join(all_final_lines))

   # normal benchmark run

   final_html_table_profile = '''
   <!DOCTYPE html>
   <html>
   <head lang="en">
      <meta charset="UTF-8">
      <style type="text/css">
         {head_embedded_style_sheet}
      </style>
      <title>Benchmark-IT: {head_module_name}</title>
   </head>
   <body>

   '''.format(head_embedded_style_sheet=get_html_template_css(), head_module_name=module_name)

   for repeat_all in range(benchmarkit__repeat):
      table = []
      for name_str, function_name_str, func_positional_arguments, func_keyword_arguments in module_tuple_of_func_tuples:
         try:
            func = getattr(loaded_module, function_name_str)
         except Exception as err:
            raise Err('_profile_functions_in_module', [
               'COULD NOT ACCESS FUNCTION ERROR: function_name_str: <{}>'.format(function_name_str),
               '  loaded_module: <{}>'.format(loaded_module),
               '    Exception: <{}>'.format(err)
            ])

         orig_func_name = getattr(func, "__name__", func)
         if use_func_name:
            name = orig_func_name
         else:
            name = name_str

         benchmark_result = _TimeIT(
            func,
            orig_func_name,
            loaded_module.__dict__,
            func_positional_arguments,
            func_keyword_arguments,
            benchmarkit__check_too_fast,
            benchmarkit__run_sec,
            name,
            perf_counter_reference_time
         ).benchmark_it(with_gc=benchmarkit__with_gc)

         table.append(benchmark_result)

      if benchmarkit__rank_by == 'best':
         table = sorted(table, key=itemgetter('best_loop_sec'))
         compare_reference = table[0]['best_loop_sec']
         for idx, dict_ in enumerate(table):
            dict_['compare'] = '{:,.3f}'.format((dict_['best_loop_sec'] / compare_reference) * 100.0)
            dict_['rank'] = '{:,}'.format(idx + 1)
            dict_['loops'] = '{:,}'.format(dict_['loops'])
            if output_in_sec:
               dict_['avg_loop_sec'] = '{:.11f}'.format(dict_['avg_loop_sec'])
               dict_['best_loop_sec'] = '{:.11f}'.format(dict_['best_loop_sec'])
               if dict_['second_best_loop_sec'] == -1.0:
                  dict_['second_best_loop_sec'] = 'NOT-MEASURED'
               else:
                  dict_['second_best_loop_sec'] = '{:.11f}'.format(dict_['second_best_loop_sec'])
               dict_['worst_loop_sec'] = '{:.11f}'.format(dict_['worst_loop_sec'])
               if dict_['second_worst_loop_sec'] == -1.0:
                  dict_['second_worst_loop_sec'] = 'NOT-MEASURED'
               else:
                  dict_['second_worst_loop_sec'] = '{:.11f}'.format(dict_['second_worst_loop_sec'])
               dict_['all_loops_time_sec'] = '{:.11f}'.format(dict_['all_loops_time_sec'])
            else:
               dict_['avg_loop_sec'] = format_time(dict_['avg_loop_sec'])
               dict_['best_loop_sec'] = format_time(dict_['best_loop_sec'])
               dict_['second_best_loop_sec'] = format_time(dict_['second_best_loop_sec'])
               dict_['worst_loop_sec'] = format_time(dict_['worst_loop_sec'])
               dict_['second_worst_loop_sec'] = format_time(dict_['second_worst_loop_sec'])
               dict_['all_loops_time_sec'] = format_time(dict_['all_loops_time_sec'])
      elif benchmarkit__rank_by == 'average':
         table = sorted(table, key=itemgetter('avg_loop_sec'))
         compare_reference = table[0]['avg_loop_sec']
         for idx, dict_ in enumerate(table):
            dict_['compare'] = '{:,.3f}'.format((dict_['avg_loop_sec'] / compare_reference) * 100.0)
            dict_['rank'] = '{:,}'.format(idx + 1)
            dict_['loops'] = '{:,}'.format(dict_['loops'])
            if output_in_sec:
               dict_['avg_loop_sec'] = '{:.11f}'.format(dict_['avg_loop_sec'])
               dict_['best_loop_sec'] = '{:.11f}'.format(dict_['best_loop_sec'])
               if dict_['second_best_loop_sec'] == -1.0:
                  dict_['second_best_loop_sec'] = 'NOT-MEASURED'
               else:
                  dict_['second_best_loop_sec'] = '{:.11f}'.format(dict_['second_best_loop_sec'])
               dict_['worst_loop_sec'] = '{:.11f}'.format(dict_['worst_loop_sec'])
               if dict_['second_worst_loop_sec'] == -1.0:
                  dict_['second_worst_loop_sec'] = 'NOT-MEASURED'
               else:
                  dict_['second_worst_loop_sec'] = '{:.11f}'.format(dict_['second_worst_loop_sec'])
               dict_['all_loops_time_sec'] = '{:.11f}'.format(dict_['all_loops_time_sec'])
            else:
               dict_['avg_loop_sec'] = format_time(dict_['avg_loop_sec'])
               dict_['best_loop_sec'] = format_time(dict_['best_loop_sec'])
               dict_['second_best_loop_sec'] = format_time(dict_['second_best_loop_sec'])
               dict_['worst_loop_sec'] = format_time(dict_['worst_loop_sec'])
               dict_['second_worst_loop_sec'] = format_time(dict_['second_worst_loop_sec'])
               dict_['all_loops_time_sec'] = format_time(dict_['all_loops_time_sec'])

      final_result_rows = ''
      for row in table:
         rank = int(row['rank'])
         if (rank % 2) == 0:
            final_td_class = 'row-even'
         else:
            final_td_class = 'row-odd'

         final_result_rows += get_html_table_row_template().format(
            td_class=final_td_class,
            td_name=row['name'],
            td_rank=row['rank'],
            td_compare=row['compare'],
            td_num_loops=row['loops'],
            td_avg_loop=row['avg_loop_sec'],
            td_best_loop=row['best_loop_sec'],
            td_second_best_loop=row['second_best_loop_sec'],
            td_worst_loop=row['worst_loop_sec'],
            td_second_worst_loop=row['second_worst_loop_sec'],
            td_all_loops_time=row['all_loops_time_sec'],
         )

      final_html_table_profile += get_html_table_template().format(
         head_title_func=module_name,
         head_module_path=module_path,
         head_module_num_functions=len(module_tuple_of_func_tuples),

         head_parameter_output_max_slashes_fileinfo='{}'.format(output_max_slashes_fileinfo),
         head_parameter_use_func_name='{}'.format(use_func_name),
         head_parameter_output_in_sec='{}'.format(output_in_sec),
         head_parameter_benchmarkit__output_source='{}'.format(benchmarkit__output_source),
         head_parameter_benchmarkit__with_gc='{}'.format(benchmarkit__with_gc),
         head_parameter_benchmarkit__check_too_fast='{}'.format(benchmarkit__check_too_fast),
         head_parameter_benchmarkit__rank_by='{}'.format(benchmarkit__rank_by),
         head_parameter_benchmarkit__run_sec='{}'.format(benchmarkit__run_sec),
         head_parameter_benchmarkit__repeat='{}'.format(benchmarkit__repeat),

         head_thead_benchmarkit__rank_by='rank-{}'.format(benchmarkit__rank_by),
         head_tfoot_benchmarkit__rank_by='rank-{}'.format(benchmarkit__rank_by),

         body_final_result_rows=final_result_rows,
      )

   final_html_table_profile += '''
   </body>
   </html>
   '''
   with open(path_join(benchmarks_dir_path, 'benchmark_it__{}.html'.format(module_name)), 'w') as file_:
      file_.write(final_html_table_profile)
