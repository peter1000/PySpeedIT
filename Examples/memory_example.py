""" Example: memory_example.py
"""


def memory_example1(ab, mul=5):
   al = [1] * (10 ** 6)
   bl = [2] * (2 * 10 ** 7)
   del bl
   cl = ab * 123456 * mul
   gl = al
   del gl
   del cl


def memory_example2():
   a = [1] * (10 ** 6)
   b = [2] * (2 * 10 ** 7)
   del b
   del a