"""
========================
PySpeedIT.disassemble_it
========================

Overview
========

Uses python's `dis.Bytecode`.

For usage see :mod:`PySpeedIT.speed_it`

**OUTPUT HTML**

   .. image:: _static/disassemble_it_results.png
      :align: center


Functions
=========

.. autofunction:: disassemble_functions_in_module
"""
from dis import Bytecode
from linecache import getlines as linecache_getlines
from os.path import (
   exists as path_exists,
   join as path_join,
)

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
         <th class="head_title" colspan="8"><b>Disassemble-IT function_name: `{head_title_func}`</b>
         </th>
      </tr>
      <tr>
         <th class="head_module_path" colspan="8">{head_module_path}
         </th>
      </tr>
      <tr>
         <th class="head_parameter" rowspan="1">
            <strong>Parameters:</strong>
         </th>
         <th class="head_parameter" colspan="7">
            <strong>output_max_slashes_fileinfo:</strong> {head_parameter_output_max_slashes_fileinfo} &nbsp;
            <strong>use_func_name:</strong> {head_parameter_use_func_name}
         </th>
      </tr>
      <tr>
         <th colspan="8">
            <br />
         </th>
      </tr>
      <tr class="head">
         <th>starts_line</th>
         <th>offset</th>
         <th>opname</th>
         <th>arg</th>
         <th>argval</th>
         <th>argrepr</th>
         <th>is_jump_target</th>
         <th>line</th>
      </tr>
      </thead>

      <tfoot>
      <tr class="head">
         <th>starts_line</th>
         <th>offset</th>
         <th>opname</th>
         <th>arg</th>
         <th>argval</th>
         <th>argrepr</th>
         <th>is_jump_target</th>
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
            <td>{td_starts_line}</td>
            <td>{td_offset}</td>
            <td>{td_opname}</td>
            <td>{td_arg}</td>
            <td>{td_argval}</td>
            <td>{td_argrepr}</td>
            <td>{td_is_jump_target}</td>
            <td>{td_line}</td>
         </tr>
   '''


def _dis_it(func):
   """ Returns a dictionary with the disassembled result

   :param func: (function)
   :return: (list) table = list_of_dictionaries
   """
   table = []

   bytecode = Bytecode(func)
   code = bytecode.codeobj
   filename = code.co_filename
   if filename.endswith(('.pyc', '.pyo')):
      filename = filename[:-1]
   if not path_exists(filename):
      raise Err('_dis_it', ['ERROR: Could not find file: {}'.format(filename)])
   all_lines = linecache_getlines(filename)

   for instr in bytecode:
      temp_dict = {}
      if instr.starts_line:
         temp_dict['starts_line'] = '{}'.format(instr.starts_line)
      else:
         temp_dict['starts_line'] = ''

      temp_dict['offset'] = '{}'.format(instr.offset)
      temp_dict['opname'] = '{}'.format(instr.opname)

      if instr.arg:
         temp_dict['arg'] = '{}'.format(instr.arg)
      else:
         temp_dict['arg'] = ''

      if instr.argval:
         temp_dict['argval'] = '{}'.format(instr.argval)
      else:
         temp_dict['argval'] = ''

      temp_dict['argrepr'] = '{}'.format(instr.argrepr)
      temp_dict['is_jump_target'] = '{}'.format(instr.is_jump_target)

      if instr.starts_line:
         temp_dict['line'] = all_lines[instr.starts_line - 1].strip()
      else:
         temp_dict['line'] = ''

      table.append(temp_dict)

   return table


def disassemble_functions_in_module(
      loaded_module,
      module_path,
      module_name,
      disassembles_dir_path,
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
      <title>Disassemble-IT: {head_module_name}</title>
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
      table = _dis_it(func)

      final_result_rows = ''
      for idx, row in enumerate(table):
         if (idx % 2) == 0:
            final_td_class = 'row-even'
         else:
            final_td_class = 'row-odd'

         final_result_rows += get_html_table_row_template().format(
            td_class=final_td_class,
            td_starts_line=row['starts_line'],
            td_offset=row['offset'],
            td_opname=row['opname'],
            td_arg=row['arg'],
            td_argval=row['argval'],
            td_argrepr=row['argrepr'],
            td_is_jump_target=row['is_jump_target'],
            td_line=row['line'],
         )

      final_html_table_profile += get_html_table_template().format(
         head_title_func=name,
         head_module_path=module_path,

         head_parameter_output_max_slashes_fileinfo='{}'.format(output_max_slashes_fileinfo),
         head_parameter_use_func_name='{}'.format(use_func_name),

         body_final_result_rows=final_result_rows,
      )

   final_html_table_profile += '''
   </body>
   </html>
   '''
   with open(path_join(disassembles_dir_path, 'disassemble_it__{}.html'.format(module_name)), 'w') as file_:
      file_.write(final_html_table_profile)
