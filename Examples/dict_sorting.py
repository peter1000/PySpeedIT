""" Example: dict_sorting.py
Mostly from: https://github.com/thisismess/python-benchmark/blob/master/examples/benchmarkDictSorting.py
"""
from operator import itemgetter
from random import shuffle


# Helper function can have a return statement
def _outer_helper(y_):
   return y_[1]


def example_pep265(data_):
   shuffle(data_)
   result = sorted(data_.items(), key=itemgetter(1))
   del result


def example_stupid(data_):
   shuffle(data_)
   result = [(key, value) for value, key in sorted([(value, key) for key, value in data_.items()])]
   del result


def example_list_expansion(data_):
   shuffle(data_)
   list_ = [(key, value) for (key, value) in data_.items()]
   result = sorted(list_, key=lambda y_: y_[1])
   del result


def example_generator(data_):
   shuffle(data_)
   list_ = ((key, value) for (key, value) in data_.items())
   result = sorted(list_, key=lambda y_: y_[1])
   del result


def example_lambda(data_):
   shuffle(data_)
   result = sorted(data_.items(), key=lambda y_: y_[1])
   del result


def example_formal_func_inner(data_):
   shuffle(data_)

   # Helper function can have a return statement
   def _inner_helper(x):
      return x[1]

   result = sorted(data_.items(), key=_inner_helper)
   del result


def example_formal_func_outer(data_):
   shuffle(data_)
   result = sorted(data_.items(), key=_outer_helper)
   del result
