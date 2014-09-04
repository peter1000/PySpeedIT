
.. index:: PySpeedIT; overview

================
Library Overview
================
**PySpeedIT** is a collection of: Benchmark-IT, Profile-IT, Line-Memory-Profile-IT, Disassemble-IT and Speed-IT.

It is useful for *python software development* and writes a html output of the results.

Benchmark-IT
------------
*Benchmark-IT* can be used *instead of python's timeit*.

It supports also timing of only selected code parts within a function using *Comment lines* with a START/END TAG.

.. code-block:: python

   START-TAG: # ::SPEEDIT::
   END-TAG:   # **SPEEDIT**


Profile-IT
----------
*Profile-IT* can be used *instead of python's profiler* and uses internally the `cProfiler`.

Line-Memory-Profile-IT
----------------------
*Line-Memory-Profile-IT* is a profiler that records the amount of memory for each line.

This code is based on parts of: `memory_profiler <https://github.com/fabianp/memory_profiler>`_.

Disassemble-IT
--------------
*Disassemble-IT* uses python's `dis.Bytecode`.

Speed-IT
--------
*Speed-IT* is a simple combination of all the above modules for easy usage.

This is the main module which should be used. For example usage see: :ref:`Code & Usage Examples <code-usage-examples>`