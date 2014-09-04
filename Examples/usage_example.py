""" Example: usage_example.py
"""
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
